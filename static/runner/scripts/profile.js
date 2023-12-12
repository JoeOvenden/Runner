document.addEventListener("DOMContentLoaded", () => {
    let followButton = document.querySelector("#follow");
    if (followButton == undefined) {
        return;
    }
    followButton.addEventListener("click", () => {
        let profile_username = document.querySelector("#username").innerHTML;
        // Send a request to toggle following
        fetch("/runner/follow", {
            method: 'PUT',
            body: JSON.stringify({
                profile_username: profile_username
            })
        }).then(response => response.json())
          .then(data => {
            console.log(data);
            let change = parseInt(data['change']);
            // Update the follower count displayed
            let followers = document.querySelector("#followers");
            followers.innerHTML = parseInt(followers.innerHTML) + change;

            // If the user has just followed
            if (change == 1) {
                followButton.innerHTML = "Unfollow";
            }
            // If the user has just unfollowed
            else {
                followButton.innerHTML = "Follow";
            }
          })
          .catch(error => console.error("Error: ", error));
    })
})