import { createMap } from './map.js';

let map = undefined;
let markers = {};
const sizeOfIcon = 48;
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
    })
};

function initMap() {
    let displayType = document.querySelector("#displayType").innerHTML;
    map = createMap("map");

    if (displayType == "route") {

        // Get the gpx file
        let gpxFile = document.querySelector("#gpxFileLoc").innerHTML;
        new L.GPX(gpxFile, {
            async: true,
            marker_options: {
                startIconUrl: '/media/icons/pin-icon-start.png',
                endIconUrl: '/media/icons/pin-icon-end.png',
                shadowUrl: null
            }
        }).on('loaded', function(e) {
            map.fitBounds(e.target.getBounds());
        }).addTo(map);
    }

    else if (displayType == "startEnd") {
        // Add start and end point maps
        ["start", "end"].forEach(markerType => {
            let markerCoordinates = [
                document.querySelector(`#${markerType}Latitude`).innerHTML,
                document.querySelector(`#${markerType}Longitude`).innerHTML
            ]
            markers[markerType] = L.marker(markerCoordinates, { icon : icons[markerType] }).addTo(map);
        });

        // Create a LatLngBounds object to encompass start and end points
        // and then fit the map to the bounds
        const bounds = L.latLngBounds(markers["start"]._latlng, markers["end"]._latlng);
        map.fitBounds(bounds);
    }
}

function addAttendEventListener() {
    let attend_text = document.querySelector("#attend");
    if (attend_text == undefined) {
        return;
    }
    attend_text.addEventListener("click", () => {
        let event_id = document.querySelector("#event_id").innerHTML;
        // Send a request to toggle following
        fetch("/attend", {
            method: 'PUT',
            body: JSON.stringify({
                event_id: event_id
            })
        }).then(response => response.json())
            .then(data => {
            let change = parseInt(data['change']);

            // Update the attendence count displayed
            // let attendence = document.querySelector("#attendence");
            // attendence.innerHTML = parseInt(attendence.innerHTML) + change;

            // If the user has just attended
            if (change == 1) {
                attend_text.innerHTML = "Unattend event";
            }
            // If the user has just unattended
            else {
                attend_text.innerHTML = "Attend event";
            }
            })
            .catch(error => console.error("Error: ", error));
    })
}

document.addEventListener("DOMContentLoaded", () => {
    initMap();
    addAttendEventListener();
});