const UMobe = require("@urvan-mobe/enterprise");

const clientId = "dhl-d2313ddb-054b-4ebc-97cf-54f2e4f8c12b";
const apiKey = "sk_439d29c0-1114-402f-aa37-24434456ad95";
const secret = "6dfc68f1-5a9f-4163-b0e0-4bda1a979afd";

const client = new UMobe(clientId, apiKey, secret);

// Example getBaysNearbyByText("Palacio de Hierro")
async function getBaysNearbyByText(text) {
    return await client.bays("MX").nearby("Zapopan, Jalisco").searchByText(text);
}

// Example getBaysNearbyByLocation("20.70887722744636, -103.41195670761607")
// Example getBaysNearbyByLocation(["20.70887722744636, "-103.41195670761607"])
// Example getBaysNearbyByLocation({ lat: "20.70887722744636, lon: "-103.41195670761607" })
// Example getBaysNearbyByLocation({ latitude: "20.70887722744636, longitude: "-103.41195670761607" })
// Example getBaysNearbyByLocation(UMobe.Location(20.70887722744636, -103.41195670761607))
async function getBaysNearbyByLocation(location) {
    return await client.bays("MX").nearby("Zapopan, Jalisco").searchByLocation(location);
}

// Example:
// const bay = await getBaysNearbyByText("Palacio de Hierro").first;
// const schedule = await UMobe.Schedule.from("2020-12-17T15:23:00.Z00").duration("20 min").done()
// or const schedule = await UMobe.Chatbot("reserva para el próximo 17 de diciembre entre las 3 y cuatro");
// const reservation = await doReservation(bay, schedule);
// await reservation.confirm();
async function doReservation(bay, schedule) {
    return await client.bays("MX").nearby("Zapopan, Jalisco").searchByLocation(location);
}

module.exports = {
    getBaysNearbyByText,
    getBaysNearbyByLocation,
    getBaysNearbyByLocation
}