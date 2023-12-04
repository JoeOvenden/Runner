document.addEventListener("DOMContentLoaded", () => {
    let follow_text = document.querySelector("#follow");
    if (follow_text == undefined) {
        return;
    }
    follow_text.addEventListener("click", () => {
        let profile_username = document.querySelector("#username").innerHTML;

        // Send a request to toggle following
        fetch("/follow", {
            method: 'PUT',
            body: JSON.stringify({
                profile_username: profile_username
            })
        }).then(response => response.json())
          .then(data => {
            let change = parseInt(data['change']);
            // Update the follower count displayed
            let followers = document.querySelector("#followers");
            followers.innerHTML = parseInt(followers.innerHTML) + change;

            // If the user has just followed
            if (change == 1) {
                follow_text.innerHTML = "Unfollow";
            }
            // If the user has just unfollowed
            else {
                follow_text.innerHTML = "Follow";
            }
          })
          .catch(error => console.error("Error: ", error));
    })
})