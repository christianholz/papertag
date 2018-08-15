// Handle drag and drop into a dropzone_element div:
// send the files as a POST request to the server

// Only start once the DOM tree is ready
if(document.readyState === "complete") {
    createDropzoneMethods();
} else {
    document.addEventListener("DOMContentLoaded", createDropzoneMethods);
}

function createDropzoneMethods() {

    let dropzone = document.getElementById("dropzone_element");
    let fileForm = document.getElementById("file_form");
    if(!'draggable' in document.createElement('span')) {
        fileForm.style.display = 'block';
        dropzone.style.display = 'none';
    }

    dropzone.ondragover = function() {
        this.className = "dropzone dragover";
        return false;
    };

    dropzone.ondragleave = function() {
        this.className = "dropzone";
        return false;
    };

    dropzone.ondrop = function(e) {
        // Stop browser from simply opening that was just dropped
        e.preventDefault();
        // Restore original dropzone appearance
        this.className = "dropzone";

        upload_files(e.dataTransfer.files)
    }
}

function upload_files(files) {
    let upload_results = document.getElementById("upload_results_element"),
        progressBar = document.getElementById("upload_progress");
    let formData = new FormData(),
        xhr = new XMLHttpRequest();

    progressBar.style.display = 'block';

    console.log("Dropped " + String(files.length) + " files.");
    for(let i=0; i < files.length; i++) {
        formData.append("file", files[i]);
    }

    formData.append("file-upload", 'Upload');

    xhr.onreadystatechange = function() {
        if(xhr.readyState === XMLHttpRequest.DONE) {
            progressBar.style.display = 'none';
        }

        console.log(xhr.response);
        upload_results.innerHTML = this.response;
    };

    xhr.upload.addEventListener("progress", function(e){
      if (e.lengthComputable) {
          progressBar.max = e.total;
          progressBar.value = e.loaded;
        console.log("add upload event-listener" + e.loaded + "/" + e.total);
      }
      else{
          upload_results.innerHTML = 'Uploading...';
      }
    }, false);

    console.log("Let's upload files: ", formData);
    xhr.open('POST', window.tag_uploadPath, true); // async = true
    xhr.send(formData);
}