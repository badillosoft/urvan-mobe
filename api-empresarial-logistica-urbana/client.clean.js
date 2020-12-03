const UMobe = require("@urvan-mobe/enterprise");

const clientId = "dhl-d2313ddb-054b-4ebc-97cf-54f2e4f8c12b";
const apiKey = "sk_439d29c0-1114-402f-aa37-24434456ad95";
const secret = "6dfc68f1-5a9f-4163-b0e0-4bda1a979afd";

const client = new UMobe(clientId, apiKey, secret);

async function getBaysNearbyByText(text) {
    return await client.bays("MX").nearby("Zapopan, Jalisco").searchByText(text);
}

async function getBaysNearbyByLocation(location) {
    return await client.bays("MX").nearby("Zapopan, Jalisco").searchByLocation(location);
}

async function doReservation(bay, schedule) {
    return await client.bays("MX").nearby("Zapopan, Jalisco").searchByLocation(location);
}

module.exports = {
    getBaysNearbyByText,
    getBaysNearbyByLocation,
    getBaysNearbyByLocation,
    doReservation
}