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
    document.querySelectorAll('[id^="like-button"]').forEach(likeButton => initLikeButton(likeButton));
    // document.querySelectorAll("#edit-post").forEach(edit_post_a => addEditPostEventListener(edit_post_a));
});


function setLikeButtonEmoji(likeButton) {
    if (likeButton.classList.contains("selected")) {
        likeButton.innerHTML = "🙂";
    }
    else {
        likeButton.innerHTML = "😐";
    }

}


function initLikeButton(likeButton) {
    setLikeButtonEmoji(likeButton);

    likeButton.addEventListener('click', event => {
        event.preventDefault();
        let comment_id = likeButton.id.split("-")[2];
        let form = new FormData(document.querySelector(`#form-${comment_id}`));
        let csrfToken = form.get('csrfmiddlewaretoken');

        // Submit the change in rating and update displayed rating and arrow selected
        fetch(`/runner/like_comment`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(comment_id)
        })
        .then(response => response.json())
        .then(data => {
            // Update displayed post rating
            let comment_rating_p = document.querySelector(`#comment-rating-${comment_id}`);
            comment_rating_p.innerHTML = data["new_rating"];

            if (likeButton.classList.contains("selected")) {
                likeButton.classList.remove("selected");
            }
            else {
                likeButton.classList.add("selected");
            }

            setLikeButtonEmoji(likeButton);
            })
        .catch(error => console.error("Error: ", error));
    });
}


function addEditPostEventListener(edit_post_a) {
    edit_post_a.addEventListener('click', () => {
        let content_div = edit_post_a.parentElement.parentElement;                      // The div containing all the post content
        let content_text_span = content_div.getElementsByClassName("post-text")[0];     // The span containing the post text

        // If the content text span already has a button inside it then the user is already editing the post so return
        if (content_text_span.getElementsByTagName("button").length != 0) {
            return;
        }

        let content_text = content_text_span.innerHTML;                                 // The post text itself
        let post_id = parseInt(content_div.getElementsByClassName("id")[0].id);

        // Creates a text area and fills with the current content text
        let text_area = document.createElement("textarea");
        text_area.maxLength = 400;
        text_area.value = content_text;

        // Button for submitting edit changes
        let submit_button = document.createElement("button");
        submit_button.innerHTML = "Submit edit";
        submit_button.addEventListener("click", () => {
            fetch("/edit_post", {
                method: 'PUT',
                body: JSON.stringify({
                    post_text: text_area.value,
                    post_id: post_id
                })
            }).then(response => {
                // If the status code is 200, then data has been sent back (because the user was logged in)
                if (response.redirected == false && response.status == 200) {
                    return response.json();
                }
                console.log(response);
                // Otherwise the user was not logged in and instead the @login_required returned the login page
                return null;
            }).then(data => {
                if (data == null) {
                    return;
                }
                content_text_span.innerHTML = text_area.value;
              })
              .catch(error => console.error("Error: ", error));
        });

        // Button for cancelling edit changes
        let cancel_button = document.createElement("button");
        cancel_button.innerHTML = "Cancel";
        cancel_button.addEventListener("click", () => {
            // Restore the span to just having the original text
            content_text_span.innerHTML = content_text;
        });

        // Clear the span and add text area and buttons
        content_text_span.innerHTML = "";
        content_text_span.appendChild(text_area);
        content_text_span.appendChild(submit_button);
        content_text_span.appendChild(cancel_button);
    });
}