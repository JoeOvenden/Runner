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

function addComponentEventListeners() {
  components = {
    "mouth": document.querySelector("#avatar-mouth"),
    "eyes": document.querySelector("#avatar-eyes")
  };

  ['mouth', 'eyes'].forEach(id => {
    document.querySelectorAll(`#${id}`).forEach(component => {
        component.addEventListener('click', () => {
          components[id].setAttribute("href", component.src);
        });
    });
  });
}

function addSaveButtonEventListener() {
  let button = document.querySelector("#save-button");
  button.addEventListener('click', () => {
    let filenames = {};
    ['mouth', 'eyes'].forEach(id => {
      let component = document.querySelector(`#avatar-${id}`);
      let filenameParts = document.querySelector(`#avatar-${id}`).href.baseVal.split("/");
      
      // If the user changed the html switching the ids around then they could a mouth component for their eyes
      // and eyes for their mouths. Therefore we must check that the component is the right type.
      let partType = filenameParts[filenameParts.length - 2];
      if (!partType.includes(id)) {
        filenames[id] = undefined;
      }
      else {
        filenames[id] = filenameParts[filenameParts.length - 1];
      }
    });

  // TODO: save parts
  fetch("/runner/edit_avatar", {
    method: 'PUT',
    body: JSON.stringify(filenames)
  }).then(response => console.log(response))
    .catch(error => console.error("Error: ", error));
    
  });
}


document.addEventListener("DOMContentLoaded", () => {
  addComponentEventListeners();
  addCollapsibleEventListeners();
  addSaveButtonEventListener();
});