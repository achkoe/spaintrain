$( function() {


const ImageList = Array(
    ["l01-p11-Substantiv.png", "l01-p11-Substantiv.png"],
    ["l02-p13-BestUnbestArtikelFormen.png", "l02-p13-BestUnbestArtikelFormen.png"],
    ["l03-p15-BestUnbestArtikelGebrauch.png", "l03-p15-BestUnbestArtikelGebrauch.png"],
    ["l04-p17-AdjektivFormen.png", "l04-p17-AdjektivFormen.png"],
    ["l05-p19-AdjektivNation.png", "l05-p19-AdjektivNation.png"],
    ["l06-p21-AdjektivStellung.png", "l06-p21-AdjektivStellung.png"],
    ["l07-p23-Steigerung1.png", "l07-p23-Steigerung1.png"],
    ["l08-p25-Steigerung2.png", "l08-p25-Steigerung2.png"],
    ["l09-p27-Steigerung3.png", "l09-p27-Steigerung3.png"],
    ["l10-p29-Adverb.png", "l10-p29-Adverb.png"]
);

    const ImageFolder = "images/";
    //const ImageFolder = "/home/achim/Dokumente/langtrain/voctrain/spaintrain/learn/grammatik_hueber/images/";
    var dialog, form, jsondialog;
    var answerField = $( "#answer" );
    var posObj = { x: 0, y: 0, listindex: null };
    var lasttext = "";
    var image_solution;
    log = console.log

    var sessionIndex;
    var lessonData;
    var imageName;
    var imageLoaded = false;
    var image_task;
    var canvas_task = $("#canvas_task").get(0);
    var ctx_task = canvas_task.getContext("2d");
    var modecontrol;
    var dragging = false;
    var dragIndex;
    var mouseX;
    var mouseY;
    var dragHoldX;
    var dragHoldY;

    Initialize();

    function TextItem(x, y, text, width, height, color, marker) {
        this.x = x;
        this.y = y;
        this.text = text;
        this.width = width;
        this.height = height;
        this.color = color;
        this.marker = marker;
    }

    function Initialize() {
        // Init local sorage if required
        if (!localStorage.getItem("lesson")) {
            InitLocalStorage();
        }
        // init session selectmenu
        $("#session").empty();
        $("#session").append(["<option/>"]).selectmenu();
        lessonData = JSON.parse(localStorage.getItem("lesson"));
        // Init lesson selectmenu
        var optionlist = []
        for (var i = 0; i < ImageList.length; i++) {
            optionlist.push("<option value='" + ImageList[i][0] + "'>" + ImageList[i][0].slice(0, -4) + "</option>");
        }
        $("#lesson").append(optionlist.join("")).selectmenu();
        modecontrol = $('input[name=modecontrol]:checked', '#controlmode').val();
        $.each($('#controlmode input'), function(index, value) {
            value.onchange = modeControl;
        });
        //loadImage(null);
    }

    function InitLocalStorage() {
        localStorage.setItem("lesson", JSON.stringify({
            "config": [
                {"name": "sizedefault", "size": 20},
                {"name": "sizecorrection", "size": 20},
                {"name": "sizeremark", "size": 20},
            ]
        }));
        for (var i = 0; i < lessonData.config.length; i++) {
            $('#' + lessonData.config[i].name).val(lessonData.config[i].size);
        }
    }

    function loadImage(eventObject) {
        /* Load images for selected lesson and initialize session selectmenu.

        Args:
            eventObject (event): not used
        */
        // get  the index of selection in lessen selectmenu.
        var selection = $("#lesson").val();
        for (var i = 0; i < ImageList.length; i++) {
            if (ImageList[i][0] == selection) {
                break;
            }
        }
        // load task and solution imaages
        imageName = ImageList[i][0];
        console.log(imageName);
        image_task = new Image();
        image_task.src = ImageFolder + imageName;
        imageName = ImageList[i][1]
        image_solution = new Image();
        image_solution.src = ImageFolder + imageName;
        image_task.onload = function() {
            canvas_task.width = image_task.width;
            canvas_task.height = image_task.height;
            ctx_task.drawImage(image_task, 0, 0);
            imageLoaded = true;
        }
        image_solution.onload = function() {
            canvas_solution.width = image_solution.width;
            canvas_solution.height = image_solution.height;
            canvas_solution.getContext("2d").drawImage(image_solution, 0, 0);
        }
        if (!lessonData.hasOwnProperty(imageName)) {
            lessonData[imageName] = {
                "sessionlist": []
            }
        }
        // initialize session selectmenu
        sessionIndex = 0;
        if (getSessionNames().indexOf("new") == -1) {
            lessonData[imageName].sessionlist.unshift({"name": "new", "textlist": []})
        }
        var optionlist = []
        for (var i = 0; i < lessonData[imageName].sessionlist.length; i++) {
            optionlist.push("<option value='" + lessonData[imageName].sessionlist[i].name + "'>" + lessonData[imageName].sessionlist[i].name + "</option>");
        }
        $("#session").empty();
        $("#session").append(optionlist.join("")).selectmenu("refresh");
    }

    function getSessionNames() {
        /* Return array with names of all sessions in current lesson.

        Returns:
            namelist (array): array with names of all sessions in current lesson.
        */
        var namelist = [];
        for (var i = 0; i < lessonData[imageName].sessionlist.length; i++) {
            namelist.push(lessonData[imageName].sessionlist[i].name);
        }
        return namelist;
    }

    function loadSession() {
        var item = $("#session")[0];
        var sessionnamelist = getSessionNames();
        var sessionName = item.options[item.selectedIndex].text;
        sessionIndex = sessionnamelist.indexOf(sessionName);
        console.log("loadSession " + sessionIndex);
        refreshObjects();
    }

    function saveSession() {
        /* Save current session.

        Save the current session in localStorage. If name of current session is 'new',
        assign a name composed of current date and runnng number to it, also update
        session selectmenu.
        */
        if (lessonData[imageName].sessionlist[sessionIndex].name == "new") {
            // new session, get a name for it using current date and an index
            var today = new Date()
            var namelist = getSessionNames();
            var name = lessonData[imageName].sessionlist[sessionIndex].name;
            // get index by looping over session names till no name is found
            var basename = "" + today.getFullYear() + "-" + (today.getMonth() + 1) + "-" + today.getDate() + "-";
            for(var i = 1; namelist.indexOf(name) != -1; i++) {
                name = basename + i;
            }
            lessonData[imageName].sessionlist[sessionIndex].name = name;
            // insert name in session combobox
            {
                var option = "<option value='" + name + "'>" + name + "</option>"
                $("#session").prepend(option).selectmenu();
                $("#session").val(name).selectmenu("refresh");
                sessionIndex = 1;
            }
        }
        // save config for session
        for (var i = 0; i < lessonData.config.length; i++) {
            lessonData.config[i].size = $( "#" + lessonData.config[i].name).val();
        }
        localStorage.setItem("lesson", JSON.stringify(lessonData));
        if (getSessionNames().indexOf("new") == -1) {
            lessonData[imageName].sessionlist.unshift({"name": "new", "textlist": []})
        }
        //console.log(lessonData);
    }

    function getCurrentFont() {
        var font = $("input[name=pencil]:checked").val()
        var size = $("#size" + font + "").val();
        color = {"default": "blue", "correction": "red", "remark": "green"}[font]
        console.log(font + " " + size);
        return {"color": color, "size": size}
    }

    function addAnswer() {
        var valid = true;
        var sessionData = lessonData[imageName].sessionlist[sessionIndex].textlist;
        var font = getCurrentFont();
        ctx_task.font = "" + font.size + "px sans-serif";
        width = ctx_task.measureText(answerField.val()).width;
        if (posObj.listindex != null) {
            sessionData[posObj.listindex].text = answerField.val();
            sessionData[posObj.listindex].width = width;
            sessionData[posObj.listindex].height = font.size;
            sessionData[posObj.listindex].color = font.color;
            sessionData[posObj.listindex].marker = 'n';
        } else {
            sessionData.push(new TextItem(posObj.x, posObj.y, answerField.val(), width, font.size, font.color, 'n'))
        }
        dialog.dialog( "close" );
        refreshObjects();
        return valid;
    }

    function findItemAtPos(pos) {
        var sessionData = lessonData[imageName].sessionlist[sessionIndex].textlist;
        foundindex = null;
        for (var index = 0; index < sessionData.length; index++) {
            var item = sessionData[index];
            if ((pos.x >= item.x) && (pos.x <= item.x + item.width)
                && (pos.y >= item.y - item.height) && (pos.y <= item.y)) {
                foundindex = index;
                break;
            }
        }
        return foundindex;
    }

    function refreshObjects() {
        var sessionData = lessonData[imageName].sessionlist[sessionIndex].textlist;
        ctx_task.clearRect(0, 0, canvas_task.width, canvas_task.height);
        ctx_task.drawImage(image_task, 0, 0);
        for (var index = 0; index < sessionData.length; index++) {
            var item = sessionData[index];
            ctx_task.fillStyle = item.color;
            ctx_task.font = "" + item.height + "px sans-serif";
            ctx_task.fillText(item.text, item.x, item.y);
            ctx_task.strokeStyle = {"n": "gray", "c": "green", "w":"red"}[item.marker];
            ctx_task.strokeRect(item.x, item.y - item.height, item.width, 1.3 * item.height);
        }
    }

    function modeControl() {
        modecontrol = $('input[name=modecontrol]:checked', '#controlmode').val();
        console.log(modecontrol);
        if (!imageLoaded) {
            return;
        }
        if (modecontrol == "btnmove") {
            canvas_task.addEventListener("mousedown", mouseDownListener, false);
            canvas_task.addEventListener("touchstart", touchStartListener, false);
        } else {
            canvas_task.removeEventListener("mousedown", mouseDownListener, false);
            canvas_task.removeEventListener("touchstart", touchStartListener, false);
            dragging = false;
            dragIndex = -1;
        }
    }

    function getMousePos(evt) {
        var rect = canvas_task.getBoundingClientRect();
        return {
            x: evt.clientX - rect.left,
            y: evt.clientY - rect.top
        };
    }

    function updateDragging(pos) {
        var foundindex = findItemAtPos(pos);
        console.log(foundindex);
        if (foundindex != null) {
            var item = lessonData[imageName].sessionlist[sessionIndex].textlist[foundindex];
            dragHoldX = pos.x - item.x;
            dragHoldY = pos.y - item.y;
            dragIndex = foundindex;
            dragging = true;
        }
    }

    function mouseDownListener(evt) {
        var pos = getMousePos(evt);
        updateDragging(pos);
        if (dragging) {
            window.addEventListener("mousemove", mouseMoveListener, false);
        }
        canvas_task.removeEventListener("mousedown", mouseDownListener, false);
        window.addEventListener("mouseup", mouseUpListener, false);
        //code below prevents the mouse down from having an effect on the main browser window:
        if (evt.preventDefault) {
            evt.preventDefault();
        } //standard
        else if (evt.returnValue) {
            evt.returnValue = false;
        } //older IE
        return false;
    }

    function mouseUpListener(evt) {
        canvas_task.addEventListener("mousedown", mouseDownListener, false);
        window.removeEventListener("mouseup", mouseUpListener, false);
        if (dragging) {
            dragging = false;
            window.removeEventListener("mousemove", mouseMoveListener, false);
        }
    }

    function mouseMoveListener(evt) {
        var pos = getMousePos(evt);
        doMove(pos);
    }

    function doMove(pos) {
        var posX, posY;
        var item = lessonData[imageName].sessionlist[sessionIndex].textlist[dragIndex];
        var minX = 0;
        var maxX = canvas_task.width - item.width;
        var minY = item.height;
        var maxY = canvas_task.height;
        mouseX = pos.x;
        mouseY = pos.y;
        //clamp x and y positions to prevent object from dragging outside of canvas
        posX = mouseX - dragHoldX;
        posX = (posX < minX) ? minX : ((posX > maxX) ? maxX : posX);
        posY = mouseY - dragHoldY;
        posY = (posY < minY) ? minY : ((posY > maxY) ? maxY : posY);
        item.x = posX;
        item.y = posY;
        refreshObjects();
    }

    //-------------------------------------------------------------------------
    function touchStartListener(evt) {
        var pos = getMousePos(evt.touches[0]);
        updateDragging(pos);
        if (dragging) {
            window.addEventListener("touchmove", touchMoveListener, false);
        }
        canvas_task.removeEventListener("touchstart", touchStartListener, false);
        window.addEventListener("touchend", touchEndListener, false);
                if (evt.preventDefault) {
            evt.preventDefault();
        } //standard
        else if (evt.returnValue) {
            evt.returnValue = false;
        } //older IE
        return false;
    }

    function touchEndListener(e) {
        canvas_task.addEventListener("touchstart", touchStartListener, false);
        window.removeEventListener("touchend", touchEndListener, false);
        if (dragging) {
            dragging = false;
            window.removeEventListener("touchmove", touchMoveListener, false);
        }
        dragIndex = -1;
    }

    function touchMoveListener(e) {
        var pos = getMousePos(e.touches[0]);
        doMove(pos);
    }
    //-------------------------------------------------------------------------

    function editItem(posObj) {
        if (posObj.listindex != null) {
            var sessionData = lessonData[imageName].sessionlist[sessionIndex].textlist;
            log("FOUND " + posObj.listindex + ": " + sessionData[posObj.listindex].text);
            answerField.val(sessionData[posObj.listindex].text);
        } else {
            answerField.val(lasttext);
        }
        dialog.dialog( "open" );
    }

    function deleteItem(foundindex) {
        lessonData[imageName].sessionlist[sessionIndex].textlist.splice(foundindex, 1);
    }

    function markItem(foundindex, correct) {
        if (foundindex == null) {
            return;
        }
        var item = lessonData[imageName].sessionlist[sessionIndex].textlist[foundindex];
        item.marker = correct ? "c": "w";
        console.log(item);
    }

    dialog = $( "#dialog-form" ).dialog({
        autoOpen: false,
        height: 200,
        width: 350,
        modal: true,
        buttons: {
            "OK": addAnswer,
            Cancel: function() {
                dialog.dialog( "close" );
            }
        },
        close: function() {
            lasttext = answerField.val();
            form[ 0 ].reset();
        }
    });

    form = dialog.find( "form" ).on( "submit", function( event ) {
        event.preventDefault();
        addAnswer();
    });

    answerField.focus(function(){
        var that = this;
        setTimeout(function(){$(that).select();},10);
    });

    $( "#clearstorage" ).button().on( "click", function() {
        console.log("clear localStorage");
        localStorage.clear();
        InitLocalStorage();
    });

    jsondialog = $("#jsondialog").dialog({
        autoOpen: false,
        modal: true,
        width:'auto',
        height:'auto',
        resizable:false,
        position: { my: "center", at: "center", of: window },
        buttons: {
            Ok: function() {
                $( this ).dialog( "close" );
            }
        },
        open: function(){
           $( "#jsoncontent" ).text(JSON.stringify(lessonData, null, 4));
           $( "#jsoncontent" ).select();
       }
    });

    $( "#showjson" ).button().on( "click", function() {
        console.log("showjson");
        jsondialog.dialog("open");

    });

    $( "#loadlesson" ).button().on("click", loadImage);
    $( "#savesession").button().on("click", saveSession);
    $( "#loadsession").button().on("click", loadSession);

    $( "#accordion" ).accordion({
        collapsible: true,
        active: false,
        heightStyle: "content",
    });

    $( "#canvas_task" ).click(function(eventObject) {
        posObj.x = eventObject.offsetX;
        posObj.y = eventObject.offsetY;
        posObj.listindex = findItemAtPos(posObj);
        if (modecontrol == "btnedit") {
            editItem(posObj);
        } else if (modecontrol == "btncorrect") {
            markItem(posObj.listindex, true);
        } else if (modecontrol == "btnwrong") {
            markItem(posObj.listindex, false);
        } else if (modecontrol == "btndelete") {
            deleteItem(posObj.listindex);
        }
        refreshObjects();
    });


} );
