// The idea of moving items was taken from
// JavaScript HTML5 Canvas example by Dan Gries, rectangleworld.com.

const ImageList = Array(
    "l01-p11-Substantiv.png",
    "l02-p13-BestUnbestArtikelFormen.png",
    "l03-p15-BestUnbestArtikelGebrauch.png",
    "l04-p17-AdjektivFormen.png",
    "l05-p19-AdjektivNation.png",
    "l06-p21-AdjektivStellung.png",
    "l07-p23-Steigerung1.png",
    "l08-p25-Steigerung2.png",
    "l09-p27-Steigerung3.png",
    "l10-p29-Adverb.png");

const _ImageFolder = "/home/achim/Dokumente/langtrain/voctrain/spaintrain/learn/grammatik_hueber/images/";
const ImageFolder = "images/";

function TextWriterApp() {
    var sessionIndex;
    var lessonData;
    var imageName;
    var imageLoaded = false;
    var image;
    var userString = "";
    var canvas = null;
    var ctx = null;
    var modecontrol;
    var dragIndex;
    var dragging;
    var mouseX;
    var mouseY;
    var dragHoldX;
    var dragHoldY;
    var showState = true;
    var showJSON = true;

    initialize();


    function initialize() {
        //localStorage.clear();
        document.querySelector("#canvas").addEventListener("click", canvasClicked, false);
        document.querySelector("#loadimage").addEventListener("click", loadImage, false);
        document.querySelector("#loadsession").addEventListener("click", loadSession, false);
        document.querySelector("#savesession").addEventListener("click", saveSession, false);
        document.getElementById("btnshow").addEventListener("click", showButton, false);
        document.getElementById("btnjson").addEventListener("click", jsonButton, false);
        showButton();
        jsonButton();

        modecontrol = document.querySelector('input[name=modecontrol]:checked', '#controlmode').value;
        itemlist = document.querySelectorAll('#controlmode input');
        for (var i = 0; i < itemlist.length; i++) {
            itemlist[i].onchange = modeControl;
        }
        if (!localStorage.getItem("lesson")) {
            localStorage.setItem("lesson", JSON.stringify({
                "config": [
                    {"name": "sizedefault", "size": 20},
                    {"name": "sizecorrection", "size": 20},
                    {"name": "sizeremark", "size": 20},
                ]
            }));
        }
        lessonData = JSON.parse(localStorage.getItem("lesson"));
        //console.log(lessonData);
        var item = document.getElementById("lesson");
        for (var i = 0; i < ImageList.length; i++) {
            var option = document.createElement("option");
            var text = document.createTextNode(ImageList[i])
            option.appendChild(text);
            item.appendChild(option);
        }
        for (var i = 0; i < lessonData.config.length; i++) {
            document.querySelector('#' + lessonData.config[i].name).value = lessonData.config[i].size;
        }
    }

    function loadImage(eventObject) {
        canvas = document.getElementById("canvas");
        ctx = canvas.getContext("2d");
        var item = document.getElementById("lesson");
        imageName = item.options[item.selectedIndex].text;
        image = new Image();
        image.src = ImageFolder + imageName;
        image.onload = function() {
            canvas.width = image.width;
            canvas.height = image.height;
            ctx.drawImage(image, 0, 0);
            imageLoaded = true;
        }
        if (!lessonData.hasOwnProperty(imageName)) {
            lessonData[imageName] = {
                "sessionlist": []
            }
        }
        sessionIndex = 0;
        if (getSessionNames().indexOf("new") == -1) {
            lessonData[imageName].sessionlist.unshift({"name": "new", "textlist": []})
        }
        item = document.getElementById("session");
        while (item.firstChild) {
            item.removeChild(item.firstChild);
        }
        for (var i = 0; i < lessonData[imageName].sessionlist.length; i++) {
            item.appendChild(getOption(lessonData[imageName].sessionlist[i].name));
        }
    }

    function getOption(label) {
        var option = document.createElement("option");
        var text = document.createTextNode(label);
        option.appendChild(text);
        return option;
    }

    function getSessionNames() {
        var namelist = [];
        for (var i = 0; i < lessonData[imageName].sessionlist.length; i++) {
            namelist.push(lessonData[imageName].sessionlist[i].name);
        }
        return namelist;
    }

    function loadSession(eventObject) {
        var item = document.getElementById("session");
        var sessionnamelist = getSessionNames();
        var sessionName = item.options[item.selectedIndex].text;
        sessionIndex = sessionnamelist.indexOf(sessionName);
        console.log("loadSession " + sessionIndex);
        refreshObjects();
    }

    function saveSession() {
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
                var item = document.getElementById("session");
                item.options[0].parentNode.insertBefore(getOption(name), item.options[0].nextSibling);
                item.selectedIndex = 1;
                sessionIndex = 1;
            }
        }
        // save config for session
        for (var i = 0; i < lessonData.config.length; i++) {
            lessonData.config[i].size = document.getElementById(lessonData.config[i].name).value;
        }
        localStorage.setItem("lesson", JSON.stringify(lessonData));
        if (getSessionNames().indexOf("new") == -1) {
            lessonData[imageName].sessionlist.unshift({"name": "new", "textlist": []})
        }
        //console.log(lessonData);
    }

    function getCurrentFont() {
        var font = document.querySelector("input[name=pencil]:checked").value;
        var size = document.querySelector("#size" + font + "").value;
        color = {"default": "blue", "correction": "red", "remark": "green"}[font]
        return {"color": color, "size": size}
    }

    function canvasClicked(eventObject) {
        console.log("pageX=" + eventObject.pageX + ", pageY=" + eventObject.pageY + ", offsetX=" + eventObject.offsetX + ", offsetY=" + eventObject.offsetY);
        var pos = {x:eventObject.offsetX, y:eventObject.offsetY}
        foundindex = findItemAtPos(pos);
        if (modecontrol == "btnedit") {
            editItem(pos, foundindex);
        } else if (modecontrol == "btncorrect") {
            markItem(foundindex, true);
        } else if (modecontrol == "btnwrong") {
            markItem(foundindex, false);
        } else if (modecontrol == "btndelete") {
            deleteItem(foundindex);
        }
        refreshObjects();
    }

    function deleteItem(foundindex) {
        lessonData[imageName].sessionlist[sessionIndex].textlist.splice(foundindex, 1);
    }

    function markItem(foundindex, correct) {
        if (foundindex == null) {
            return;
        }
        var item = lessonData[imageName].sessionlist[sessionIndex].textlist[foundindex];
        item.m = correct ? "c": "w";
        console.log(item);
    }

    function findItemAtPos(pos) {
        var sessionData = lessonData[imageName].sessionlist[sessionIndex].textlist;
        foundindex = null;
        for (var index = 0; index < sessionData.length; index++) {
            var item = sessionData[index];
            if ((pos.x >= item.x) && (pos.x <= item.x + item.w)
                && (pos.y >= item.y - item.h) && (pos.y <= item.y)) {
                foundindex = index;
                break;
            }
        }
        return foundindex;
    }

    function editItem(pos, foundindex) {
        var string, foundindex, width;
        var sessionData = lessonData[imageName].sessionlist[sessionIndex].textlist;
        var font = getCurrentFont();
        string = foundindex == null ? userString : sessionData[foundindex].text
        string = prompt("Please enter answer", string);
        if (string == null) {
            return;
        }

        userString = string.replace("!!", '\u00A1').replace("??", '\u00BF').replace("~n", '\u00F1');
        ctx.font = "" + font.size + "px sans-serif";
        width = ctx.measureText(string).width;
        //console.log("" + width + ", " + string);
        if (foundindex == null) {
            // add new item
            foundindex = sessionData.length;
            sessionData.push({x: pos.x, y:pos.y});
        }
        sessionData[foundindex].text = userString;
        sessionData[foundindex].w = width;
        sessionData[foundindex].h = font.size
        sessionData[foundindex].c = font.color
        sessionData[foundindex].m = "n";
    }

    function refreshObjects() {
        var sessionData = lessonData[imageName].sessionlist[sessionIndex].textlist;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(image, 0, 0);
        for (var index = 0; index < sessionData.length; index++) {
            var item = sessionData[index];
            ctx.fillStyle = item.c;
            ctx.font = "" + item.h + "px sans-serif";
            ctx.fillText(item.text, item.x, item.y);
            ctx.strokeStyle = {"n": "gray", "c": "green", "w":"red"}[item.m];
            ctx.strokeRect(item.x, item.y - item.h, item.w, 1.3 * item.h);
        }
    }

    function getMousePos(evt) {
        var rect = canvas.getBoundingClientRect();
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
        canvas.removeEventListener("mousedown", mouseDownListener, false);
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
        canvas.addEventListener("mousedown", mouseDownListener, false);
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
        var maxX = canvas.width - item.w;
        var minY = item.h;
        var maxY = canvas.height;
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
        canvas.removeEventListener("touchstart", touchStartListener, false);
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
        canvas.addEventListener("touchstart", touchStartListener, false);
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

    function modeControl() {
        modecontrol = document.querySelector('input[name=modecontrol]:checked', '#controlmode').value;
        console.log(modecontrol);
        if (!imageLoaded) {
            return
        }
        if (modecontrol == "btnmove") {
            canvas.addEventListener("mousedown", mouseDownListener, false);
            canvas.addEventListener("touchstart", touchStartListener, false);
        } else {
            canvas.removeEventListener("mousedown", mouseDownListener, false);
            canvas.removeEventListener("touchstart", touchStartListener, false);
            dragging = false;
            dragIndex = -1;
        }
    }

    function showButton() {
        //console.log("showButton");
        pnl = document.getElementById("pnlshow");
        pnl.style.display = showState ? "none": "block";
        showState = !showState;
        document.getElementById("btnshow").textContent = showState ? "\u2191" : "\u2193";
        if (!imageLoaded) {
            pnl.textContent = "No image loaded!"
            return;
        }
        while (pnl.firstChild) {
            pnl.removeChild(pnl.firstChild);
        }
        var dt, dd, text, par, quote, color;
        var dl = document.createElement("dl");
        for (label in lessonData) {
            if (!lessonData.hasOwnProperty(label)) continue;
            if (label == "config") continue;
            console.log(label);
            dt = document.createElement("dt");
            dt.appendChild(document.createTextNode(label));
            dl.appendChild(dt);
            dd = document.createElement("dd");
            dl.appendChild(dd);
            text = "";
            for (session in lessonData[label].sessionlist) {
                session = lessonData[label].sessionlist[session];
                if (session.name == "new") continue;
                result = {"c": 0, "w": 0, "n": 0};
                for (item in session.textlist) {
                    result[session.textlist[item].m] += 1;
                }
                par = document.createElement("p");
                quote = (100.0 * result.c / (result.w + result.c));
                color = quote > 80.0 ? "good": (quote < 50.0 ? "bad": "medium");
                par.innerHTML = session.name + ": correct " + result.c + ", wrong: " + result.w + ", quote: "
                                + "<span class='" + color + "'>" + quote.toFixed(1) + "%" + "</span>";
                dd.appendChild(par);
            }
        }
        pnl.appendChild(dl);
    }

    function jsonButton() {
        //console.log("jsonButton");
        pnl = document.getElementById("pnljson");
        pnl.style.display = showJSON ? "none": "block";
        showJSON = !showJSON;
        document.getElementById("btnjson").textContent = showJSON ? "\u2191" : "\u2193";
        if (!imageLoaded) {
            pnl.textContent = "No image loaded!"
            return;
        }
        pnl.textContent = JSON.stringify(lessonData, null, 4);
    }
}


window.addEventListener("load", windowLoadHandler, false);

function windowLoadHandler() {
    TextWriterApp();
}
