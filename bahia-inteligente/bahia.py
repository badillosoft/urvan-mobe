# Flask - Microframework para construir un servidor web
from flask import Flask
from flask_cors import CORS
# JSON - Formato de transporte de datos
import json
# OpenCV - Librería de procesamiento de imágenes
import cv2
# Threading - Librería para el manejo de hilos y computación concurrente
import threading
# Librerías para el maneno de fechas y horas
import time
from datetime import datetime, date
# GPIO - Librería para el manejo de pines de la placa Raspberry Pi
import RPi.GPIO as GPIO
# Regex - Librería para el manejo de expresiones regulares y patrones en textos
import re

# Creamos el servidor
app = Flask(__name__)

# Permitimos el acceso remoto
CORS(app)

# Cremos un contexto de estado interno
context = {
    "count": 0,
    "at": datetime.now().isoformat(),
    "libre": False,
    "servicio": None,
    "carga": 0,
    "history": [],
    "qrBahia": {
        "id": "Why are you",
        "count": 0,
        "at": datetime(2020, 1, 1, 0, 0, 0).isoformat(),
        "elapsed": 1
    },
    "qrTransporte": {
        "id": ["Hello mate!", "looking at this?"],
        "currentId": "none",
        "count": 0,
        "at": datetime(2020, 1, 1, 0, 0, 0).isoformat(),
        "elapsed": 1
    },
}

# Registramos los pines físicos de la placa
pins = {
    "A1": 15,
    "A2": 13,
    "A3": 11,
    "A4": 12,
    "B1": 35,
    "B2": 33,
    "B3": 31,
    "B4": 29
}

# Descompone una fecha en formato ISO en una tupla de valores numéricos
# (año, mes, día, hora, minuto, segundo)
def extract_isodate(isodate):
    match = re.search("(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})", isodate)
    year = match.group(1)
    month = match.group(2)
    day = match.group(3)
    hour = match.group(4)
    minute = match.group(5)
    second = match.group(6)
    return (int(year), int(month), int(day), int(hour), int(minute), int(second))
    
# Calcula el tiempo transcurrido en segundos de una fecha ISO a la fecha y hora actual
def elapsed(isodate):
    now = datetime.now().isoformat()
    y2, m2, d2, hh2, mm2, ss2 = extract_isodate(now)
    y1, m1, d1, hh1, mm1, ss1 = extract_isodate(isodate)
    
    date2 = datetime(y2, m2, d2, hh2, mm2, ss2)
    date1 = datetime(y1, m1, d1, hh1, mm1, ss1)
    return abs(date2 - date1).seconds

# Define el trabajo principal que será ejecutado en un hilo en paralelo
def worker():
    # Incrementa el contador global de procesos
    global count
    print("worker started")
    # Inicializa la captura de la cámara de video
    cap = cv2.VideoCapture(0)
    # Inicializa la placa de pines de la Raspberry Pi
    GPIO.setmode(GPIO.BOARD)
    # Inicializa cada pin registrado
    for name, pin in pins.items():
        GPIO.setup(pin, GPIO.OUT)
        print("{}/{} setup".format(name, pin))
    # Crea un lazo indeterminado mientras el sistema no sea detenido
    while not stopped:
        # Incrementa el contador del contexto
        context["count"] += 1
        # Guarda la fecha ISO de última lectura
        context["at"] = datetime.now().isoformat()
        # Captura el siguiente frame de la cámara
        ret, frame = cap.read()
        # Almacena la información del frame
        #context["frame"] = frame
        # Detecta los códigos QR
        det = cv2.QRCodeDetector()
        hasQR, texts, codes, points = det.detectAndDecodeMulti(frame)
        # Si hay un QR detectado
        if hasQR:
            for text in texts:
                if text.strip() != "":
                    # Comprueba si el QR es de la bahía
                    if text == "Why are you":
                        # Actualiza el contexto de la bahía
                        context["qrBahia"]["count"] = context["count"]
                        context["qrBahia"]["at"] = datetime.now().isoformat()
                    
                    # Comprueba si el QR es de un transporte registrado
                    for name in context["qrTransporte"]["id"]:
                        if text == name:
                            # Actualiza el contexto del transporte detectado
                            context["qrTransporte"]["currentId"] = name
                            context["qrTransporte"]["at"] = datetime.now().isoformat()
                            context["qrTransporte"]["elapsed"] = elapsed(context["qrTransporte"]["at"])
        
        # Mide el tiempo transcurrido a la última lectura de la bahía detectada
        context["qrBahia"]["elapsed"] = elapsed(context["qrBahia"]["at"])
        # Mide el tiempo transcurrido a la última lectura del transporte detectado
        context["qrTransporte"]["elapsed"] = elapsed(context["qrTransporte"]["at"])
        
        # Consulta el último estado del contexto
        libre = context["libre"]
        servicio = context["servicio"]
        
        # Checa si hay un transporte detectado y cambia el estado a "en servicio"
        if context["qrTransporte"]["elapsed"] < 1:
            context["servicio"] = True
        
        # Checa si se ha perdido la lectura de la bahía y cambia el estado a "ocupado"
        if context["qrBahia"]["elapsed"] >= 1:
            context["libre"] = False
        # Checa si la bahía es detectada y cambia el estado a "libre, fuera de servicio"
        else:
            context["libre"] = True
            context["servicio"] = False
            
        # Si hay cambio en el estado "libre/ocupado"
        if context["libre"] != libre:
            # Si está libre
            if context["libre"]:
                # Prende el LED "libre" y apaga "ocupado"
                GPIO.output(pins["B1"], GPIO.HIGH)
                GPIO.output(pins["B2"], GPIO.LOW)
            # Si está ocupado
            else:
                # Prende el LED "ocupado" y apaga "libre"
                GPIO.output(pins["B1"], GPIO.LOW)
                GPIO.output(pins["B2"], GPIO.HIGH)
            
            # Agrega al hitórico la el estado nuevo "libre" u "ocupado" con su fecha de lectura
            # y el identificador de la bahía
            context["history"].append({
                "at": datetime.now().isoformat(),
                "id": context["qrBahia"]["id"],
                "type": "bahia",
                "action": "libre" if context["libre"] else "ocupado"
            })
        
        # Si hay cambio en el estado "en servicio"
        if context["servicio"] != servicio:
            # Si está en servicio
            if context["servicio"]:
                # Prende el LED "en servicio"
                GPIO.output(pins["B3"], GPIO.HIGH)
            # Si no está en servicio
            else:
                # Apaga el LED "en servicio"
                GPIO.output(pins["B3"], GPIO.LOW)
            
            # Agrega al hitórico la el estado nuevo "en servicio" o "fuera de servicio" 
            # con su fecha de lectura y el identificador del transporte identificado
            context["history"].append({
                "at": datetime.now().isoformat(),
                "id": context["qrTransporte"]["currentId"],
                "type": "transporte",
                "action": "servicio" if context["servicio"] else "fuera"
            })
            
    # Cuándo se detiene el proceso se libera la cámara y la placa de pines
    cap.release()
    GPIO.cleanup()
    print("worker stopped")
    
# Retiene el estado interno del trabajo paralelo
started = True    
stopped = False
# Crea un hilo para ejecutar la carga de trabajo repetitiva
t = threading.Thread(target=worker)
# Comienza la captura de trabajo
t.start()

# Envía el contexto actual de la bahía
@app.route('/')
def home():
    return json.dumps(context)

# Reinicia la operación de la bahía
@app.route('/start')
def start():
    global started, stopped, t
    if not started:
        t = threading.Thread(target=worker)
        t.start()
        started = True
        stopped = False
    return 'started {} stopped {}'.format(started, stopped)

# Finaliza la operación de la bahía (libera los recursos)
@app.route('/stop')
def stop():
    global started, stopped
    if started:
        started = False
        stopped = True
        t.join()
    return 'started {} stopped {}'.format(started, stopped)

# Inicializa el servidor
app.run(port=5000, host="0.0.0.0")