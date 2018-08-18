/* JavaScript for webtrain. */


var g_storage;
var g_lesson;
var g_session;
const NEW = "new";
const localStorageKey = "webtrain";


$(document).ready(function() {
    console.log(location.hostname);
    $(".lesson").hide();
    $(".solution").hide();

    // initialize local storage if not already done
    if (!localStorage.getItem(localStorageKey)) {
        localStorage.setItem(localStorageKey, JSON.stringify({}));
    }
    g_storage = JSON.parse(localStorage.getItem(localStorageKey));

    // try to synchronize with server
    $.ajaxSetup({timeout: 5000});
    var jqxhr = $.post( "http://" + location.hostname + ":8080/json/",
        JSON.stringify(g_storage),
        null, "json")
    .done(function(data) {
        localStorage.setItem(localStorageKey, JSON.stringify(data));
        console.log( "data synced" );
        init(true);
    })
    .fail(function() {
        init(false);
        console.log( "data not synced" );
    })
    .always(function() {
        console.log( "complete" );
    });
});

function init(synced) {
    g_storage = JSON.parse(localStorage.getItem(localStorageKey));

    // make point sliders
    $(".slider").each(function(index) {
        $( this ).slider({range: "min", max: 2, value: 0});
        $( this ).find(".ui-slider-handle").attr("tabindex", index + 1);
    });
    // make table of content
    $( "h1" ).each(function() {
        var item = $( this ).text()
        var item_id = $( this ).attr("id");

        if (!g_storage[item_id]) {
            g_storage[item_id] = {};
        }
        var lessondata = g_storage[item_id];
        var sessionlist = Object.keys(lessondata);
        sessionlist = sessionlist.sort().reverse();

        var link = $( "<a/>", {html: item, "class": "toc", href: "#", "onclick": "show_lesson('" + item_id + "')"} );
        var select = $("<select id='s" + item_id + "'/>")
        select.append( $("<option>" + NEW + "</option>", {value: 0}))
        for (var i = 0; i < sessionlist.length; i++) {
            select.append( $("<option>" + (i + 1) + " - " + sessionlist[i] + "</option>", {value: i + 1}))
        }
        var tablerow = $( "<div/>", {"class": "rtablerow", id: "tr" + item_id});
        tablerow.append(link);
        tablerow.append(select);
        $( "#toc" ).append(tablerow);
    });
    // prettify table of contents
    $( ".toc" ).wrap( $( "<div class='rtablecell'/>" ) );
    $( "select" ).wrap( $( "<div class='rtablecell'/>" ) );
    // initialize views
    show_toc();
    $( "#wait" ).hide();
    $( "#main" ).removeClass("hidden")
    $.sparkline_display_visible();
    // show sync hint
    $( "#sync" ).removeClass("hidden")
    $("#synctext").text((synced ? "S" : "Not s") + "ynchronized with server");
    $("#sync").fadeOut(4000);
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
    for (key in g_storage) {
        var lessondata = g_storage[key];
        show_statistic(key, lessondata);
    }
    $("#toc").show();
    $.sparkline_display_visible();
}

function show_statistic(whichid, lessondata) {
    var statistic = [];
    if (Object.keys(lessondata).length <= 1) return;
    for (var session in lessondata) {
        // filter solutions, they have a key starting with 's'
        var solutions = Object.keys(lessondata[session]).filter(key => key.startsWith('s'));
        var points = 0;
        for (var i = 0; i < solutions.length; i++) {
            points += lessondata[session][solutions[i]]
        }
        statistic.push(points);
    }
    //console.log(statistic);
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
    //console.log(lesson);
    var sessionobj
    // get the selected session
    var session = $( "#s" + lesson + " option:selected").text();
    //console.log(session)
    if (session == NEW) {
        sessionobj = g_storage[lesson];
        sessionobj[session] = {}
        g_storage[lesson] = sessionobj;
    } else {
        session = session.substring(session.indexOf('-') + 1).trim();
    }
    g_lesson = lesson;
    g_session = session;
    var item_id;
    // load data from session
    var lessondata = g_storage[g_lesson];
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
    var lessondata = g_storage[g_lesson];
    var sessiondata = lessondata[g_session];
    if (g_session == NEW) {
        session = new Date().toISOString();
        delete lessondata[g_session];
        g_session = session;
        session = "" + $( "#s" + g_lesson + " option" ).length + " - " + session;
        $( "#s" + g_lesson ).children()[0].remove();
        $( "#s" + g_lesson).prepend( $("<option>" + session + "</option>", {value: 0})); // value?
        $( "#s" + g_lesson).prepend( $("<option>" + NEW + "</option>", {value: 0})); // value?
    }
    var item, item_id;
    $("#d" + g_lesson + " input[type=text]").each(function(index, element) {
        item_id = $(this).attr("id");
        item = $(this).val();
        sessiondata[item_id] = item;
        //console.log("" + item_id + ": " + item);
    });
    $("#d" + g_lesson + " input[type=radio]").each(function(index, element) {
        item_id = $(this).attr("id");
        item = $(this).prop("checked")
        sessiondata[item_id] = item;
        //console.log("" + item_id + ": " + item);
    });
    $("#d" + g_lesson + " .slider").each(function() {
        item_id = $(this).attr("id");
        sessiondata[item_id] = $(this).slider("value");
    });
    lessondata[g_session] = sessiondata;
    g_storage[g_lesson] = lessondata;
    localStorage.setItem(localStorageKey, JSON.stringify(g_storage))
    // show_local_storage();
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
    for (key in g_storage) {
        var lesson = g_storage[key];
        sdiv.append( $( "<h2/>", {text: key} ) );
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
