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
        fetch("/runner/attend", {
            method: 'PUT',
            body: JSON.stringify({
                event_id: event_id
            })
        }).then(response => response.json())
            .then(data => {

            // Get the change in attendence count
            // change = 1 means the user has attended the event
            // change = -1 means the user has unattended the event
            let change = parseInt(data['change']);

            // Alter displayed attendence count
            let attendence_count = document.querySelector("#attendence_count");
            attendence_count.innerHTML = parseInt(attendence_count.innerHTML) + change;

            // Get the users username from the navbar and their profile card from that
            let username = document.querySelector("#logged-in-user").innerHTML;
            let profileCard = document.querySelector(`#${username}`);
            console.log("Profile card: ", profileCard);
            console.log("Username:", username);

            // If the user has just attended then change the button text accordingly
            // and make visible the user's profile card in people going
            if (change == 1) {
                attend_text.innerHTML = "Unattend event";
                profileCard.classList.remove("hidden");
            }

            // If the user has just unattended then change the button text accordingly
            // and hide the user's profile card in people going
            else {
                attend_text.innerHTML = "Attend event";
                profileCard.classList.add("hidden");
            }
            })
            .catch(error => console.error("Error: ", error));
    })
}

function addCollapsibleEventListeners() {
    let coll = document.getElementsByClassName("collapsible");
    let i;
    for (i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function() {
          this.classList.toggle("active");
          var content = this.nextElementSibling;
          if (content.style.maxHeight){
            content.style.maxHeight = null;
          } 
          else {
            content.style.maxHeight = "50vh";
          }
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initMap();
    addAttendEventListener();
    addCollapsibleEventListeners();
});