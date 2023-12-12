// Creates and returns a map
export function createMap(mapId, coordinates=[51.50649, -0.12673]) {
    let map = L.map(mapId).setView(coordinates, 13);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
    return map;
}

// Returns icons
export function getIcons(sizeOfIcon=48) {
    let icons = {
        "start": L.icon({
            iconUrl: '../../media/icons/pin-icon-start.png',
            iconSize: [sizeOfIcon, sizeOfIcon],
            iconAnchor: [sizeOfIcon / 2, sizeOfIcon],
        }),
        "end": L.icon({
            iconUrl: '../../media/icons/pin-icon-end.png',
            iconSize: [sizeOfIcon, sizeOfIcon],
            iconAnchor: [sizeOfIcon / 2, sizeOfIcon], 
        }),
        "centre": L.icon({
            iconUrl: '../../media/icons/pin-icon-centre.png',
            iconSize: [sizeOfIcon, sizeOfIcon],
            iconAnchor: [sizeOfIcon / 2, sizeOfIcon], 
        })
    };
    return icons;
}