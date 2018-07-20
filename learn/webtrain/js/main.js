$(document).ready(function(){
    /* Hier der jQuery-Code */
    init();
});


var g_lesson;
var g_session;
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
    var sessionobj
    // get the selected session
    var session = $( "#s" + lesson + " option:selected").text();
    if (session == NEW) {
        // create a new session name
        session = (new Date()).toISOString();
        console.log(session);
        // add session name to localStorage
        sessionobj = JSON.parse(localStorage.getItem(lesson))
        sessionobj[session] = {}
        localStorage.setItem(lesson, JSON.stringify(sessionobj));
        console.log(localStorage);
        // append new session name to select
        $( "#s" + lesson).append( $("<option>" + session + "</option>", {value: 0})); // value?
    }
    // load data from session

    //
    g_lesson = lesson;
    g_session = session;
    // show and hide things
    $("#toc").hide();
    $("#d" + lesson).show();
    $("#control_t").show();
    $("#control_b").show();
    $(".show").each(function(index, element) {
        $(this).text( "Show" );
    });
    $("#d" + lesson + " .solution").hide();
}

function save() {
    //TODO: set id of note to lesson_counter_x !!!
    //TODO: set all names of radio buttons belonging to one group to the same
    //TODO: set labels for all radio buttons, remove value from radio buttons, remove leading numbers from radio buttons where approbiate
    console.log("saving lesson " + g_lesson + " session " + g_session);
    var lesson = JSON.parse(localStorage.getItem(g_lesson));
    console.log("lesson=" + lesson +"|")
    var result = lesson[g_session];
    console.log("result=" + result +"|")
    var item, item_id;
    $("#d" + g_lesson + " input[type=text]").each(function(index, element) {
        item_id = $(this).attr("id");
        item = $(this).val();
        result[item_id] = item;
        console.log("" + item_id + ": " + item);
    });
    $("#d" + g_lesson + " input[type=radio]").each(function(index, element) {
        item_id = $(this).attr("id");
        item = $(this).prop("checked")
        result[item_id] = item;
        console.log("" + item_id + ": " + item);
    });
    lesson[g_session] = result;
    localStorage.setItem(g_lesson, JSON.stringify(lesson));
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