import { createMap, getIcons } from './map.js';
import { getLocation } from './geolocation.js';

let map = undefined;
let centreMarker = undefined;
let markers = {};
let circle = undefined;
let coordinateInput = undefined;    // Hidden HTML coordinate input element
let coordinates = [51, 0];
let icons = getIcons(48);

function changePosition(latlng) {
    // Change position of marker and circle and update hidden html coordinate input element
    centreMarker.setLatLng(latlng);
    circle.setLatLng(latlng);
    coordinateInput.value = latlng["lat"].toFixed(5) + "," + latlng["lng"].toFixed(5);
}

function addEventMarkers() {
    // Add marker to map for every event on the page

    // Get an array containing all <p> elements for the event latlngs
    let coordinateElements = Array.from(document.querySelectorAll('[id^="event-latlng"]'));

    for(let coordinateElement of coordinateElements) {
        let latlng = coordinateElement.innerHTML.split(",");
        let marker = L.marker(latlng).addTo(map);
        let id = coordinateElement.id.split("-")[2];
        let parent = coordinateElement.parentElement;
        let distance = parent.querySelector("#distance").innerHTML;
        let title = parent.querySelector("#title").innerHTML;
        let date = parent.querySelector("#date").innerHTML;
        marker.bindPopup(`
            <div class="marker-popup">
                <a href="event/${id}"><p>Event: ${title}</p></a>
                <p>Distance: ${distance}</p>
                <p>Date: ${date}</p>
            </div>
        `);
        markers[id] = marker;
    }
}

function getLatlngAsDict(latlngStr) {
    // Takes latlng in from "lat,lng" and returns it as a dict
    if (latlngStr == "") {
        return undefined;
    }
    let latlngArray = latlngStr.replace(/\s/g, "").split(",");
    let latlng = {
        "lat": parseFloat(latlngArray[0]),
        "lng": parseFloat(latlngArray[1])
    };
    return latlng;
}

function initPosition(position) {       // Set map location to device location
    let latlng = {
        "lat": position.coords.latitude,
        "lng": position.coords.longitude
    };
    coordinates = latlng;
    changePosition(latlng);
    map.fitBounds(circle.getBounds());
}

function showError(error) {
    switch (error.code) {
        case error.PERMISSION_DENIED:
            coordinateInput.value = coordinates[0] + ", " + coordinates[1];
            break;
        case error.POSITION_UNAVAILABLE:
            alert("Location information is unavailable.");
            break;
        case error.TIMEOUT:
            alert("The request to get user location timed out.");
            break;
        case error.UNKNOWN_ERROR:
            alert("An unknown error occurred.");
            break;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    /*
     * If coordinate input is not empty, then this means the form has been submitted
     * and so the coordinates from the form are to be kept. 
     * We shouldn't use the user's location
     * 
     * Otherwise we use the default coordinates and then after everything is defined,
     * we get the user's coordinates and change things accordingly.
     */
    coordinateInput = document.querySelector("#id_coordinates");
    let getUserLocation = true;
    if (coordinateInput.value != "") {
        coordinates = getLatlngAsDict(coordinateInput.value);
        getUserLocation = false;
    }
    map = createMap("map", coordinates);             // Create the map

    coordinateInput.addEventListener('change', () => {
        // Get longitude and latitude from input element as an array
        // Removes whitespace and splits into lat and lng by the comma
        let latlng = getLatlngAsDict(coordinateInput.value);
        changePosition(latlng);
        map.fitBounds(circle.getBounds());
    });

    map.on('click', e => {      // When the map is clicked
        // Here we specifically do not want to fit the maps bounds to the circles bounds
        // as this feels very annoying to use.
        // Hence we setview using the marker to keep the same level of zoom.
        changePosition(e.latlng);
        map.setView(centreMarker._latlng);
    });

    centreMarker = L.marker(coordinates, { icon : icons["centre"] }).addTo(map);
    let radiusInputElement = document.querySelector("#id_search_radius");

    circle = L.circle(coordinates, {
        color: 'red',
        fillColor: '#f03',
        fillOpacity: 0.2,
        radius: radiusInputElement.value * 1000,
        weight: 2,
    }).addTo(map);

    // When the user changes the radius in the input element, change the circle radius on the map
    // and then change the zoom based on the size of the circle.
    radiusInputElement.addEventListener('change', () => {
        circle.setRadius(radiusInputElement.value * 1000);
        map.fitBounds(circle.getBounds());
    })

    if (getUserLocation) {
        getLocation(initPosition, showError);
    }
    else {
        map.fitBounds(circle.getBounds());
    }
    addEventMarkers();
});