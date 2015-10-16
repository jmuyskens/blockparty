// set up drag drop data
var dataTextArea = document.getElementById('drop');

dataTextArea.addEventListener("drag", function( event ) {

}, false);

dataTextArea.addEventListener("dragstart", function( event ) {
  // store a ref. on the dragged elem
  dragged = event.target;
  // make it half transparent
  event.target.style.opacity = .5;
}, false);

dataTextArea.addEventListener("dragend", function( event ) {
  // reset the transparency
  event.target.style.opacity = "";
}, false);

/* events fired on the drop targets */
dataTextArea.addEventListener("dragover", function( event ) {
  // prevent default to allow drop
  event.preventDefault();
}, false);

dataTextArea.addEventListener("dragenter", function( event ) {
  // highlight potential drop target when the draggable element enters it
  if ( event.target.id == "drop" ) {
      event.target.className = "dropzone";
  }
}, false);

dataTextArea.addEventListener("dragleave", function( event ) {
  // reset background of potential drop target when the draggable element leaves it
  if ( event.target.id == "drop" ) {
      event.target.className = "";
  }

}, false);

dataTextArea.addEventListener("drop", function( event ) {
  // prevent default action (open as link for some elements)
  event.preventDefault();
  // move dragged elem to the selected drop target
  if ( event.target.className == "dropzone" ) {
    event.target.style.background = "";
  }

  var dt = event.dataTransfer;
  var files = dt.files;
  var reader = new FileReader();

  fd = new FormData();

  for (var i = 0; i < files.length; i++) {
  	fd.append('file', files[i]);
  }

  var createAjax = new XMLHttpRequest();
  createAjax.open('POST', 'create', true);

  var uploadAjax = new XMLHttpRequest();
  var id;

  createAjax.addEventListener('load', function(e) {
  	id = JSON.parse(createAjax.responseText).id;

  	uploadAjax.open('POST', 'block/' + id, true);
  	uploadAjax.send(fd);
  });

  uploadAjax.addEventListener('load', function(e) {
  	window.location.href += 'block/' + id;
  });

  createAjax.send();
}, false);
