$(document).ready(function(){
    /* Hier der jQuery-Code */
    init();
});


var g_lesson;
const NEW = "new"

function init() {
    $(".lesson").hide();
    $(".solution").hide();

    $( "h1" ).each(function(index, element) {
        var item = $( this ).text()
        var item_id = $( this).attr("id");

        if (!localStorage.getItem(item_id)) {
            localStorage.setItem(item_id, JSON.stringify({}));
        }
        var sessionlist = Object.keys(JSON.parse(localStorage.getItem(item_id)));

        var link = $( "<a/>", {
            html: item,
            "class": "toc",
            href: "#",
            "onclick": "show_lesson('" + item_id + "')",
        });
        var select = $("<select id='s" + item_id + "'/>")
        select.append( $("<option>" + NEW + "</option>", {value: 0}))
        for (var i = 0; i < sessionlist.length; i++) {        
            select.append( $("<option>" + sessionlist[i] + "</option>", {value: i + 1}))
        }
        $( "#toc" ).append( $("<p>").append(link).append(select));
        show_toc();
    });
}

function show_toc() {
    /*  
        Hide current lesson
        Hide control divs
        Show table of contents 
    */
    $("#d" + g_lesson).hide();
    $("#control_t").hide();
    $("#control_b").hide();
    g_lesson = "toc";
    $("#toc").show();
}

function show_lesson(lesson) {
    /*
        Hide table of contents
        Show current lesson
        Show control divs
        Reset Show buttons and hide solution 
    */
    console.log(lesson);
    // get the selected session
    var session = $( "#s" + lesson + " option:selected").text();
    if (session == NEW) {
        // create a new session name
        session = (new Date()).toISOString();
        console.log(session);
        // add session name to localStorage
        var sessionobj = JSON.parse(localStorage.getItem(lesson))
        sessionobj[session] = {}
        localStorage.setItem(lesson, JSON.stringify(sessionobj));
        console.log(localStorage);
        // append new session name to select
        $( "#s" + lesson).append( $("<option>" + session + "</option>", {value: 0})); // value?
    }
    $("#toc").hide();
    $("#d" + lesson).show();
    $("#control_t").show();
    $("#control_b").show();
    g_lesson = lesson;
    $(".show").each(function(index, element) {
        $(this).text( "Show" );
    });
    $("#" + g_lesson + " .solution").hide();
}

function save() {
    console.log("save");
}

function home() {
    show_toc();
}

function show_solution() {
    $(".show").each(function(index, element) {
        $(this).text( $(this).text() == "Show" ? "Hide" : "Show");
    });
    $("#d" + g_lesson + " .solution").toggle();
}