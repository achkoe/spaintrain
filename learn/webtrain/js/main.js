/*
TODO: update statistic with show toc
*/

$(document).ready(function() {
    /* Hier der jQuery-Code */
    init();
});


var g_lesson;
var g_session;
var g_item_id_list = []
const NEW = "new"

function init() {
    var t0, t1;
    t0 = performance.now();

    $(".lesson").hide();
    $(".solution").hide();

    $(".slider").each(function() {
        var item_id = $(this).attr("id");
        //console.log($(this));
        $(this).slider({
            range: "min",
            max: 2,
            value: 0,
        });
    });


    $( "h1" ).each(function(index, element) {
        var item = $( this ).text()
        var item_id = $( this ).attr("id");
        g_item_id_list.push(item_id);

        if (!localStorage.getItem(item_id)) {
            localStorage.setItem(item_id, JSON.stringify({}));
        }
        var lessondata = JSON.parse(localStorage.getItem(item_id));
        var sessionlist = Object.keys(lessondata);

        var link = $( "<a/>", {html: item, "class": "toc", href: "#", "onclick": "show_lesson('" + item_id + "')"} );
        var select = $("<select id='s" + item_id + "'/>")
        select.append( $("<option>" + NEW + "</option>", {value: 0}))
        for (var i = 0; i < sessionlist.length; i++) {
            select.append( $("<option>" + sessionlist[i] + "</option>", {value: i + 1}))
        }
        var tablerow = $( "<div/>", {"class": "rtablerow", id: "tr" + item_id});
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
    $.sparkline_display_visible();
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
    console.log(g_item_id_list);
    g_lesson = "toc";
    for (var i = 0; i < g_item_id_list.length; i++) {
        var lessondata = JSON.parse(localStorage.getItem(g_item_id_list[i]));
        show_statistic(g_item_id_list[i], lessondata);
    }
    $("#toc").show();
    $.sparkline_display_visible();
}

function show_statistic(whichid, lessondata) {
    var statistic = [];
    for (var session in lessondata) {
        // filter solutions, they have a key starting with 's'
        var solutions = Object.keys(lessondata[session]).filter(key => key.startsWith('s'));
        var points = 0;
        for (var i = 0; i < solutions.length; i++) {
            points += lessondata[session][solutions[i]]
        }
        statistic.push(points);
    }
    if (statistic.length == 0) {
        return;
    }
    console.log(statistic);
    var text = "" + points + "/" + solutions.length;


    // show trend with arrows or similar
    var trend;
    if ((statistic.length < 2 ) || (statistic[statistic.length - 1] == statistic[statistic.length - 2])) {
        trend = $('<button class="ui-button ui-widget ui-corner-all trend" title=""><span class="ui-icon ui-icon-arrowthick-2-e-w"></span>' + text + '</button>');
    } else 
    if (statistic[statistic.length - 1] > statistic[statistic.length - 2]) {
        trend = $('<button class="ui-button ui-widget ui-corner-all trend" title=""><span class="ui-icon ui-icon-arrowthick-1-ne"></span>' + text + '</button>');
    } else 
    if (statistic[statistic.length - 1] < statistic[statistic.length - 2]) {
        trend = $('<button class="ui-button ui-widget ui-corner-all trend" title=""><span class="ui-icon ui-icon-arrowthick-1-se"></span>' + text + '</button>');
    }
    var bar = $( "<span class='bar'>&nbsp;</span>" );
    bar.sparkline(statistic, { type: 'bar', stackedBarColor: ['blue', 'green', 'yellow', 'red'],  });
    $( "#tr" + whichid + " .bar").remove();
    $( "#tr" + whichid + " .trend").remove();
    $( "#tr" + whichid ).append(trend);
    $( "#tr" + whichid ).append(bar);
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
    var item_id;
    // load data from session
    var lessondata = JSON.parse(localStorage.getItem(g_lesson));
    var sessiondata = lessondata[g_session];
    $("#d" + g_lesson + " input[type=text]").each(function(index, element) {
        item_id = $(this).attr("id");
        $(this).val(sessiondata.hasOwnProperty(item_id) ? sessiondata[item_id] : "")
    });
    $("#d" + g_lesson + " input[type=radio]").each(function(index, element) {
        item_id = $(this).attr("id");
        $(this).prop("checked", sessiondata.hasOwnProperty(item_id) ? sessiondata[item_id] : false);
        $(this).button("refresh");
    });

    $("#d" + g_lesson + " .slider").each(function() {
        item_id = $(this).attr("id");
        $(this).slider("value", sessiondata.hasOwnProperty(item_id) ? sessiondata[item_id] : 0);
    });
    // show and hide things
    $("#toc").hide();
    $("#d" + lesson).show();
    $("#control_t").show();
    $("#control_b").show();
    $(".show").removeClass( "ui-icon-circle-close" );
    $(".show").addClass( "ui-icon-lightbulb" );
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
    $("#d" + g_lesson + " .slider").each(function() {
        item_id = $(this).attr("id");
        sessiondata[item_id] = $(this).slider("value");
    });
    lessondata[g_session] = sessiondata;
    localStorage.setItem(g_lesson, JSON.stringify(lessondata));
    show_local_storage();
}

function home() {
    show_toc();
}

function show_solution() {
    $(".show").toggleClass("ui-icon-lightbulb");
    $(".show").toggleClass("ui-icon-circle-close");
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