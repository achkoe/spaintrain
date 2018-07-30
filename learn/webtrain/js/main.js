$(document).ready(function() {
    /* Hier der jQuery-Code */
    init();
});


var g_lesson;
var g_session;
const NEW = "new"

function init() {
    var t0, t1;
    t0 = performance.now();

    $(".lesson").hide();
    $(".solution").hide();

    $( "h1" ).each(function(index, element) {
        var item = $( this ).text()
        var item_id = $( this ).attr("id");

        if (!localStorage.getItem(item_id)) {
            localStorage.setItem(item_id, JSON.stringify({}));
        }
        var sessionlist = Object.keys(JSON.parse(localStorage.getItem(item_id)));

        var link = $( "<a/>", {html: item, "class": "toc", href: "#", "onclick": "show_lesson('" + item_id + "')"} );
        var select = $("<select id='s" + item_id + "'/>")
        select.append( $("<option>" + NEW + "</option>", {value: 0}))
        for (var i = 0; i < sessionlist.length; i++) {
            select.append( $("<option>" + sessionlist[i] + "</option>", {value: i + 1}))
        }
        var tablerow = $( "<div class='rtablerow'/>" );
        tablerow.append(link);
        tablerow.append(select);
        $( "#toc" ).append(tablerow);
    });
    $( ".toc" ).wrap( $( "<div class='rtablecell'/>" ) );
    $( "select" ).wrap( $( "<div class='rtablecell'/>" ) );
    show_toc();
    //show_local_storage();
    $( "#wait" ).hide();
    $( "#main" ).removeClass("hidden")
    t1 = performance.now();
    console.log("Time took " + (t1 - t0) + " milliseconds.")
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
        session = "" + $( "#s" + lesson + " option" ).length + " (" + (new Date()).toISOString() + ")";
        console.log(session);
        // add session name to localStorage
        sessionobj = JSON.parse(localStorage.getItem(lesson))
        sessionobj[session] = {}
        localStorage.setItem(lesson, JSON.stringify(sessionobj));
        console.log(localStorage);
        // append new session name to select
        $( "#s" + lesson).append( $("<option>" + session + "</option>", {value: 0})); // value?
    }
    g_lesson = lesson;
    g_session = session;
    // load data from session
    var lessondata = JSON.parse(localStorage.getItem(g_lesson));
    var sessiondata = lessondata[g_session];
    $("#d" + g_lesson + " input[type=text]").each(function(index, element) {

        item_id = $(this).attr("id");
        $(this).val(sessiondata.hasOwnProperty(item_id) ? sessiondata[item_id] : "")
    });
    $("#d" + g_lesson + " input[type=radio]").each(function(index, element) {
        item_id = $(this).attr("id");
        $(this).prop("checked", sessiondata.hasOwnProperty(item_id) ? sessiondata[item_id] : false)
    });

    //
    // show and hide things
    $("#toc").hide();
    $("#d" + lesson).show();
    $("#control_t").show();
    $("#control_b").show();
    $(".show").each(function(index, element) {
        $(this).text( "Mostrar" );
    });
    $("#d" + lesson + " .solution").hide();
}

function save() {
    console.log("saving lesson " + g_lesson + " session " + g_session);
    var lessondata = JSON.parse(localStorage.getItem(g_lesson));
    var sessiondata = lessondata[g_session];
    var item, item_id;
    $("#d" + g_lesson + " input[type=text]").each(function(index, element) {
        item_id = $(this).attr("id");
        item = $(this).val();
        sessiondata[item_id] = item;
        console.log("" + item_id + ": " + item);
    });
    $("#d" + g_lesson + " input[type=radio]").each(function(index, element) {
        item_id = $(this).attr("id");
        item = $(this).prop("checked")
        sessiondata[item_id] = item;
        console.log("" + item_id + ": " + item);
    });
    lessondata[g_session] = sessiondata;
    localStorage.setItem(g_lesson, JSON.stringify(lessondata));
    show_local_storage();
}

function home() {
    show_toc();
}

function show_solution() {
    $(".show").each(function(index, element) {
        $(this).text( $(this).text() == "Mostrar" ? "Ocultar" : "Mostrar");
    });
    $("#d" + g_lesson + " .solution").toggle();
}

function show_local_storage() {
    var sdiv = $("#ls");
    if (sdiv.length != 0) {
        sdiv.remove()
    }
    $("body").append($("<div/>", {id: "ls"}));
    sdiv = $("#ls");
    for ( var i = 0, len = localStorage.length; i < len; ++i ) {
        var lesson = localStorage.key(i);
        sdiv.append( $( "<h2/>", {text: lesson} ) );
        lesson = JSON.parse(localStorage.getItem(lesson));
        console.log(lesson);

        var dl = $("<dl/>");
        Object.keys(lesson).forEach(function(key, index) {
            dl.append( $( "<dt/>", {html: key} ));
            var session = lesson[key];
            Object.keys(session).forEach(function(key, index) {
               dl.append( $( "<dd/>", {html: "" + key + ": " + session[key]} ))
            });
        });
        sdiv.append(dl);
    }

}