(function() {

    // getElementById
    function $id(id) {
        return document.getElementById(id);
    }

    // output information
    function Output(msg) {
        var m = $id("messages");
        m.innerHTML = msg + m.innerHTML;
    }

    // file drag hover
    function FileDragHover(e) {
        e.stopPropagation();
        e.preventDefault();
        e.target.className = (e.type == "dragover" ? "hover" : "");
    }

    // file selection
    function FileSelectHandler(e) {

        // cancel event and hover styling
        FileDragHover(e);

        // fetch FileList object
        var files = e.target.files || e.dataTransfer.files;

        // process all File objects
        for (var i = 0, f; f = files[i]; i++) {
            //ParseFile(f);
            UploadFile(f);
        }
    }

    // output file information
    function ParseFile(file) {
        Output(
            "<p>File information: <strong>" + file.name +
            "</strong> type: <strong>" + file.type +
            "</strong> size: <strong>" + file.size +
            "</strong> bytes</p>"
        );
    }

    // upload files
    function UploadFile(file) {
        var myformdata = $id("myform");
        var formData = new FormData(myformdata);
        
        // following line is not necessary: prevents running on SitePoint servers
        if (location.host.indexOf("sitepointstatic") >= 0) return

        var xhr = new XMLHttpRequest();
        if (xhr.upload) {
            
            formData.append('multi_file',file)
            // create progress bar
            var o = $id("progress");
            var progress = o.appendChild(document.createElement("p"));
            progress.appendChild(document.createTextNode("upload " + file.name));

            // progress bar
            xhr.upload.addEventListener("progress", function(e) {
                var pc = parseInt(100 - (e.loaded / e.total * 100));
                progress.style.backgroundPosition = pc + "% 0";
                progress.innerHTML = (100 - pc)+"%";
				//if (pc<10) {progress.remove();}
            }, false);

            // file received/failed
            xhr.onreadystatechange = function(e) {
                if (xhr.readyState == 4) {
                    progress.className = (xhr.status == 200 ? "success" : "failure");
					if (xhr.status == 200) {
						progress.innerHTML=100+'%';
						ajax(myformdata.action.replace('upload_data','view'),[],'progress');
					}
                }
            };

            // start upload
            //Output("<p>Form Action <strong>" + myformdata.action)
            xhr.open("POST", myformdata.action, true);
            xhr.setRequestHeader("X_FILENAME", file.name);
            xhr.send(formData);
        }

    }

    // initialize
    function Init() {

        var filedrag = $id("filedrag"),
            fileselect = $id("data_file_file");
            submitbutton = $id("submit_record__row");

        // file select
        fileselect.addEventListener("change", FileSelectHandler, false);

        // is XHR2 available?
        var xhr = new XMLHttpRequest();
        if (xhr.upload) {

            // file drop
            filedrag.addEventListener("dragover", FileDragHover, false);
            filedrag.addEventListener("dragleave", FileDragHover, false);
            filedrag.addEventListener("drop", FileSelectHandler, false);
            filedrag.style.display = "block";

            // remove submit button
            submitbutton.style.display = "none";
        }
    }

    // call initialization file
    if (window.File && window.FileList && window.FileReader) {
        Init();
    }


})();
