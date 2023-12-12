
import { createMap } from './map.js';
import { getLocation } from './geolocation.js';

// Initially set start and end coordinates to null
let markers = {
    "start": null,
    "end": null
};

var initialCoordinates = [51.505, -0.09];

function updateInputCoordinates() {
    ["start", "end"].forEach(mapType => {
        ["Latitude", "Longitude"].forEach(latOrLng => {
    
            // Get coordinate input element and add event listener
            let coordinateInput = document.querySelector(`#${mapType}${latOrLng}`);
            if (latOrLng == "Latitude") {
                coordinateInput.value = initialCoordinates[0];
            }
            else {
                coordinateInput.value = initialCoordinates[1];
            }
        })
    })
}

function initialiseMaps(position) {
    initialCoordinates = [position.coords.latitude.toFixed(5), position.coords.longitude.toFixed(5)];
    createMaps(initialCoordinates);
    updateInputCoordinates();
}

getLocation(initialiseMaps);

// Declare DOM elements for distance, duration and pace (defined when DOM content is loaded)
let distanceInput = undefined;
let durationInput = undefined;
let paceInput = undefined;

let maps = {};

// Hide file selection row, because initially no radio button has been clicked
let file_upload_row = document.querySelector("#id_route").parentElement.parentElement;
file_upload_row.style.display = "none";

function setRowDisplay(mapType, display) {
    /*
     * Changes a maps display type.
     * When the maps go from being hidden to shown, map.invalidateSize() needs to be
     * called, otherwise they don't know how big they are and the tiling doesn't work.
     */
    document.querySelector(`#${mapType}MapRow`).style.display = display;
    if (display == "table-row") {
        maps[mapType].invalidateSize();
    }
}

function showGpx() {
    // Shows gpx
    file_upload_row.style.display = "table-row";
    setRowDisplay("route", "table-row");

    // Hides start and end point maps
    setRowDisplay("start", "none");
    setRowDisplay("end", "none");
}

function showStartEnd() {
    // Shows start and end point maps
    setRowDisplay("start", "table-row");
    setRowDisplay("end", "table-row");

    // Hides gpx
    file_upload_row.style.display = "none";
    setRowDisplay("route", "none");
}

// Moves map marker
function moveMapMarker(mapType, latlng) {
    markers[mapType].setLatLng(latlng);
    maps[mapType].setView(latlng);
}

// Moves map marker and changes the values in the lat and lng input elements
function setMapMarker(latlng, mapType) {
    moveMapMarker(mapType, latlng);
    document.querySelector(`#${mapType}Latitude`).value = latlng["lat"].toFixed(5);
    document.querySelector(`#${mapType}Longitude`).value = latlng["lng"].toFixed(5);
}

function createMaps(initialCoordinates) {
    // Creates a map for the start and end coordinates and adds event listener
    ["start", "end"].forEach(mapType => {
        maps[mapType] = createMap(`${mapType}Map`, initialCoordinates);
        markers[mapType] = L.marker(initialCoordinates).addTo(maps[mapType]);
        maps[mapType].on('click', e => setMapMarker(e.latlng, mapType));
    });

    // Create route map
    maps["route"] = createMap("routeMap", initialCoordinates);
}

function durationToSeconds(duration) {
    // Converts duration in format "hh:mm" to seconds
    let paceParts = duration.split(":");
    let hours = parseInt(paceParts[0]);
    let minutes = parseInt(paceParts[1]);
    return hours * 3600 + minutes * 60;
}

function paceToSeconds(pace) {
    // Converts pace in format "mm:ss" to seconds
    let paceParts = pace.split(":");
    let minutes = parseInt(paceParts[0]);
    let seconds = parseInt(paceParts[1]);
    return (minutes * 60) + seconds;
}

function secondsToPace(paceInSeconds) {
    // Converts a pace in seconds to the format "mm:ss"
    let minutes = Math.floor(paceInSeconds / 60);
    let seconds = Math.floor(paceInSeconds % 60);
    let paceString = minutes.toString().padStart(2, '0') + ":" + seconds.toString().padStart(2, '0');
    return paceString;
}

function calculateDuration(pace, distance) {
    // Takes pace in format "mm:ss" and distance in kms and gives duration in format "hh:mm"
    let paceInSeconds = paceToSeconds(pace);
    let distanceInKilometers = parseFloat(distance);

    let durationInSeconds = paceInSeconds * distanceInKilometers;
    // Convert duration to "mm:ss" format
    let hours = Math.floor(durationInSeconds / 3600);
    let minutes = Math.floor((durationInSeconds % 3600) / 60);
    let durationString = hours.toString().padStart(2, '0') + ":" + minutes.toString().padStart(2, '0');
    return durationString;
}

function setDuration(pace) {
    // Sets duration of DOM element based off of distance and pace
    durationInput.value = calculateDuration(pace, distanceInput.value);
}

function setPace(duration) {
    // Sets pace of DOM element based off of distance and duration
    let durationInSeconds = durationToSeconds(duration);
    let paceInSeconds = durationToSeconds(duration) / distanceInput.value;
    paceInput.value = secondsToPace(paceInSeconds);
}

document.addEventListener('DOMContentLoaded', function() {

    // Get DOM elements for distance, duration and pace
    distanceInput = document.querySelector("#id_distance");
    durationInput = document.querySelector("#id_duration");
    paceInput = document.querySelector("#id_pace");

    // When the distance changes, change the duration to match based on the pace
    distanceInput.addEventListener('change', () => {
        setDuration(paceInput.value);
    });

    // When the duration changes, change the pace to match
    durationInput.addEventListener('change', () => {
        setPace(durationInput.value);
    });

    // When the pace changes, change the duration to match
    paceInput.addEventListener('change', () => {
        setDuration(paceInput.value);
    });

    // Adds event listeners to upload method radio buttons
    document.querySelectorAll('input[name="uploadMethod"]').forEach(function(radio) {
        radio.addEventListener('change', function() {
            // If upload method is by gpx, then show file upload row and route map row
            if (this.value === 'gpx') {
                showGpx();
            } 
            // Otherwise for manual, show start and end point map rows
            else if (this.value === 'manual') {
                showStartEnd();
            }
        });
    });


    // Event listener for when a file is uploaded
    document.querySelector("#id_route").addEventListener('change', event => {

        // Get the gpx file
        let gpxFile = event.target.files[0];

        // Setup reader with onload function
        let reader = new FileReader();
        reader.onload = function() {
            let gpxData = reader.result;
            new L.GPX(gpxData, {
                async: true,
                marker_options: {
                    startIconUrl: 'media/icons/pin-icon-start.png',
                    endIconUrl: 'media/icons/pin-icon-end.png',
                    shadowUrl: null
                }
            }).on('addpoint', e => {
                // Start and end markers set
                setMapMarker(e.point._latlng, e.point_type);
            }).on('loaded', function(e) {
                maps["route"].fitBounds(e.target.getBounds());
                distanceInput.value = (e.target.get_distance() / 1000).toFixed(1);
                durationInput.value = calculateDuration(paceInput.value, distanceInput.value);
            }).addTo(maps["route"]);
        }

        // Gpx file is read and onload function is triggered
        reader.readAsText(gpxFile);
    });


    // Adds event listeners for each coordinate input element
    ["start", "end"].forEach(mapType => {
        ["Latitude", "Longitude"].forEach(latOrLng => {

            // Get coordinate input element and add event listener
            let coordinateInput = document.querySelector(`#${mapType}${latOrLng}`);
            if (latOrLng == "Latitude") {
                coordinateInput.value = initialCoordinates[0];
            }
            else {
                coordinateInput.value = initialCoordinates[1];
            }

            coordinateInput.addEventListener('change', () => {
                let latlng = markers[mapType]._latlng;
                if (latOrLng == "Latitude") {
                    latlng["lat"] = coordinateInput.value;
                }
                else {
                    latlng["lng"] = coordinateInput.value;
                }
                moveMapMarker(mapType, latlng);
            });
        })
    })
});
