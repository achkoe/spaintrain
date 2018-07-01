console.log("Here");

function goto(index) {
    console.log(index);
    var e = document.getElementsByName("main");
    document.getElementById("lesson").value = "" + index;
    var session = document.getElementById("" + index);
    var v = session.options[session.selectedIndex].value;
    e[0].action = "session/" + index + "/" + v;
    console.log(v);
    e[0].submit();
}

function save(index) {
    console.log(index);
    var e = document.getElementsByName("main");
    var session = document.getElementById("session").value;
    e[0].action = e[0].action + "/" + session;
    console.log(session);
    e[0].submit();
}

function home() {
    var e = document.getElementsByName("main");
    e[0].action = "/";
    e[0].submit();
}

function showsolution() {var clsElements = document.querySelectorAll(".mySpeshalClass");
    console.log("show"); 
    var clsElements = document.querySelectorAll(".solution");
    var btnSolution = document.getElementById("show");
    var style;
    if (btnSolution.innerHTML == "Show") {
        btnSolution.innerHTML = "Hide";
        style = "block";
    }
    else {
        btnSolution.innerHTML = "Show";
        style = "none";
    }
    for (i = 0; i < clsElements.length; i++) {
        clsElements[i].style.display = style;
    }
}