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
  }).then(response => {
    if (response.status == 200) {
      document.querySelector("#success-message").innerHTML = "Avatar successfully saved.";
    }
  })
    .catch(error => console.error("Error: ", error));
    
  });
}

function isHexColor(str) {
  // Regular expression to match a hexadecimal color code. Checks for just 6 digit color codes.
  const hexColorRegex = /^#([0-9A-Fa-f]{6})$/;

  // Test if the input string matches the regular expression
  return hexColorRegex.test(str);
}

function changeFaceColour(color) {
  let face = document.querySelector("#face");
  face.setAttribute('fill', color);
}

function addColorPickingEventListeners() {
  let colorPicker = document.querySelector("#colorPicker");
  let colorInput = document.querySelector("#colorInput");

  // When the color picker is changed, change the value in the color input and the face color
  colorPicker.addEventListener('change', e => {
    changeFaceColour(e.target.value);
    colorInput.setAttribute('value', e.target.value);
  });

  // When the color input is changed, if valid change the color of the color picker and face colour.
  colorInput.addEventListener('change', e => {
    if (isHexColor(e.target.value)) {
      changeFaceColour(e.target.value);
      colorPicker.value = e.target.value;
    }
  });
}


document.addEventListener("DOMContentLoaded", () => {
  addComponentEventListeners();
  addCollapsibleEventListeners();
  addSaveButtonEventListener();
  addColorPickingEventListeners();
});