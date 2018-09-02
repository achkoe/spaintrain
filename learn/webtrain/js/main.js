var g_storage;
var g_modified;
var g_lesson;
var g_session;
const localStorageKey = "webtrain";
const NEW = "new";
const maxPoints = 2;


$(document).ready(function() {

    // --- initialize local storage if not already done ---
    if (!localStorage.getItem(localStorageKey)) {
        localStorage.setItem(localStorageKey, JSON.stringify({}));
    }
    g_storage = JSON.parse(localStorage.getItem(localStorageKey));
    // --- set up message panel
    $("body").append($("<div/>", {id:"sync", class:"ui-widget hidden"})
        .append($("<div/>", {class:"ui-state-error ui-corner-all", style:"padding: 0 .7em;"})
            .append($("<p/>")
                .append(
                    $("<span/>", {class:"ui-icon ui-icon-alert", style:"float: left; margin-right: .3em;"}),
                    $("<span/>", {id:"synctext"})
    ))));
    sync_with_server(true);
});

function init() {
    var elem, toc, select, item_id;
    g_storage = JSON.parse(localStorage.getItem(localStorageKey));
    // --- set up dialog ---
    $("body").append($("<div/>", {id:"dialog", title: "Quit without saving?"})
        .append($("<p/>", {text:"All changes are lost. Are you sure?"})
            .append($("<span/>", {class:"ui-icon ui-icon-alert", style:"float:left; margin:12px 12px 20px 0;"}))))
    $("#dialog").dialog({
        autoOpen: false, resizable: false, height: "auto", width: 400, modal: true,
        buttons: {
            "Ok": function() {
                $( this ).dialog( "close" );
                show_toc();
            },
            Cancel: function() {
                $( this ).dialog( "close" );
            }
        }
    });
    // --- set up table of contents ---
    toc = $("<div/>", {id:"toc", class:"rtable"});
    for (var header in ld) {
        item_id = parseInt(header);
        if (!g_storage[item_id]) {
            g_storage[item_id] = {};
        } else {
            if (NEW in g_storage[item_id]) {
                alert("Fund");
            }
        }
        toc.append($("<div/>", {class:"rtablerow", id:`tr${item_id}`})
            .append(
                $("<div/>", {class:"rtablecell"}).append($("<a>", {html:header, href:"#" + item_id, onclick:`show_lesson(${item_id}, '${header}')`})),
                $("<div/>", {id:`o${item_id}`, class:"rtablecell"}).append(build_session_select(item_id))
        ));
    }
    $("body").append(toc);
    // --- set up upper and lower toolbar ---
    elem = $("<div/>", {class: "control"});
    elem.append($("<button/>", {class:"ui-button ui-widget ui-corner-all ui-button-icon-only", title:"Guardar", onclick:"save()", html:"&nbsp;"})
        .append($("<span/>", {class:"ui-icon ui-icon-disk"})));
    elem.append($("<button/>", {class:"ui-button ui-widget ui-corner-all ui-button-icon-only", title:"Inicio", onclick:"home()", html:"&nbsp;"})
        .append($("<span/>", {class:"ui-icon ui-icon-home"})));
    elem.append($("<button/>", {class:"ui-button ui-widget ui-corner-all ui-button-icon-only", title:"Mostrar", onclick:"show_solution()", html:"&nbsp;"})
        .append($("<span/>", {class:"ui-icon ui-icon-lightbulb show"})));
    $("body").append(elem);
    $("body").append($("<div/>", {id:"session"}));
    $("body").append(elem.clone());
    show_toc();
}

function build_session_select(lesson) {
    var lessondata = g_storage[lesson];
    var sessionlist = Object.keys(lessondata);
    sessionlist = sessionlist.sort().reverse();

    select = $(`<select id='s${lesson}'/>`)
    select.append( $(`<option>${NEW}</option>`))
    for (var i = 0; i < sessionlist.length; i++) {
        select.append( $(`<option> ${sessionlist.length - i} - ${sessionlist[i]} </option>`))
    }
    return select;
}

function show_lesson(lesson, lessonname) {
    //console.log(lessonname);
    var re = new RegExp("\\[([^\\]]+)\\]", "g");

    // --- get the selected session ---
    var session = $(`#s${lesson} option:selected`).text();
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
    // --- set up session ---
    var taskindex = 0;
    $("#session").empty();
    // render lesson
    for (var header in ld[lessonname]) {
        $("#session").append($("<h1/>", {html:header}));
        var columncnt = 0;
        var container = $("<div/>", {class:"flex-container"});
        var column = $("<div/>", {class:"column"});
        for (var index in ld[lessonname][header]) {
            var item = ld[lessonname][header][index];
            if (item.startsWith('.bc')) {
                columncnt += 1;
                if (columncnt > 1) {
                    container.append(column);
                }
                column = $("<div/>", {class:"column"});
                continue;
            }
            var matches = new Array();
            while ((match = re.exec(item)) !== null) {
                matches.push(match);
            }
            var solutionlist = new Array();
            var replacement = ""
            var pos = 0;
            var name;
            var taskclass = "taskns"
            for (var matchindex = 0; matchindex < matches.length; matchindex++) {
                taskclass = "task";
                replacement += item.slice(pos, matches[matchindex]["index"])
                pos = matches[matchindex]["index"];
                //name = '' + parseInt(lessonname) + '_' + taskindex + '_' + matchindex;
                name = `${parseInt(lessonname)}_${taskindex}_${matchindex}`;
                if (matches[matchindex][1].startsWith(":")) {
                    var enumitemlist = matches[matchindex][1].slice(2).split('|');
                    //console.log(enumitemlist);
                    replacement += "<span class='rbtask cbradio'>"
                    for (var enumindex = 0; enumindex < enumitemlist.length; enumindex++) {
                        var id = `${name}_${enumindex}`;
                        if (enumitemlist[enumindex].startsWith('!')) {
                            enumitemlist[enumindex] = enumitemlist[enumindex].slice(1);
                            solutionlist.push(enumitemlist[enumindex]);
                        }
                        replacement += `<input required="required" type="radio" id="${id}" name="${name}"/><label for="${id}">${enumitemlist[enumindex]}</label>`
                    }
                    replacement += "</span>"
                } else {
                    replacement += `<input required="required" type="text" id="${name}" name="${name}" size="${matches[matchindex][1].length}"/>`
                    solutionlist.push(matches[matchindex][1]);
                }
                pos += matches[matchindex][0].length;
            }
            //console.log(item);
            //console.log(pos);
            replacement += item.slice(pos);
            column.append($("<p/>", {class:taskclass, html:replacement}));
            if (taskclass == "task") {
                column.append($("<div/>", {class:"flex-container solution"})
                    .append($("<div/>", {class:"slider", id:`s_${lesson}_${taskindex}`}),
                            $("<div/>", {class:"column"})
                            .append($("<span/>", {html: solutionlist.join(', ')}))));
            }
            $("#session").append(container.append(column));
            taskindex += 1;
        }
    }
    $( ".cbradio input" ).checkboxradio({icon: false});
    $(".slider").each(function(index) {
        $( this ).slider({range: "min", max: 2, value: 0});
        $( this ).find(".ui-slider-handle").attr("tabindex", index + 1);
        $( this ).on("slidechange", function(event) {g_modified = true;});
    });
    // --- load data from session ---
    var item_id;
    var lessondata = g_storage[g_lesson];
    var sessiondata = lessondata[g_session];
    $("#session input[type=text]").each(function(index, element) {
        item_id = $(this).attr("id");
        $(this).val(sessiondata.hasOwnProperty(item_id) ? sessiondata[item_id] : "")
    });
    $("#session input[type=radio]").each(function(index, element) {
        item_id = $(this).attr("id");
        $(this).prop("checked", sessiondata.hasOwnProperty(item_id) ? sessiondata[item_id] : false);
        $(this).button("refresh");
    });
    $("#session .slider").each(function() {
        item_id = $(this).attr("id");
        $(this).slider("value", sessiondata.hasOwnProperty(item_id) ? sessiondata[item_id] : 0);
    });
    //--- add change monitor ---
    $("input").each(function() {
        $(this).on("input change", function(event) {g_modified = true;});
    });
    g_modified = false;
    // --- show and hide ---
    $("#toc").hide();
    $(".show").removeClass( "ui-icon-circle-close" );
    $(".show").addClass( "ui-icon-lightbulb" );
    $("#session .solution").hide();
    $("#session").show();
    $(".control").show();
}

function show_solution() {
    $(".show").toggleClass("ui-icon-lightbulb");
    $(".show").toggleClass("ui-icon-circle-close");
    $("#session .solution").toggle();
}

function save() {
    console.log(`saving lesson ${g_lesson}, session ${g_session}`);
    var lessondata = g_storage[g_lesson];
    var sessiondata = lessondata[g_session];
    if (g_session == NEW) {
        delete lessondata[g_session];
        g_session = new Date().toISOString();
    }
    var item, item_id;
    $("#session input[type=text]").each(function(index, element) {
        item_id = $(this).attr("id");
        item = $(this).val();
        sessiondata[item_id] = item;
        //console.log("" + item_id + ": " + item);
    });
    $("#session input[type=radio]").each(function(index, element) {
        item_id = $(this).attr("id");
        item = $(this).prop("checked")
        sessiondata[item_id] = item;
        //console.log("" + item_id + ": " + item);
    });
    $("#session .slider").each(function() {
        item_id = $(this).attr("id");
        sessiondata[item_id] = $(this).slider("value");
    });
    if (g_session.indexOf(NEW) !== -1) alert("g_session =" + g_session);
    console.log("g_session = " + g_session);
    lessondata[g_session] = sessiondata;
    g_storage[g_lesson] = lessondata;
    localStorage.setItem(localStorageKey, JSON.stringify(g_storage))

    $(`#s${g_lesson}`).remove();
    $(`#o${g_lesson}`).append(build_session_select(g_lesson));

    g_modified = false;
    sync_with_server(false);
}

function home() {
    if (g_modified) {
        $("#dialog").dialog("open");
    } else {
        show_toc();
    }
}

function show_toc() {
    $("#session").hide();
    $(".control").hide();
    show_statistic();
    $("#toc").show();
}

function show_statistic() {
    for (whichid in g_storage) {
        var lessondata = g_storage[whichid];

        var statistic = [];
        if (Object.keys(lessondata).length <= 0) continue;
        for (var session in lessondata) {
            // filter solutions, they have a key starting with 's'
            var solutions = Object.keys(lessondata[session]).filter(key => key.startsWith('s'));
            var points = 0;
            for (var i = 0; i < solutions.length; i++) {
                points += lessondata[session][solutions[i]]
            }
            statistic.push(points);
        }
        console.log(statistic);
        var text = `${points}/${maxPoints * solutions.length}`;
        var title = statistic.slice(0, 11).reverse().join('|')
        var icon;
        // show trend with arrows or similar
        if ((statistic.length < 2 ) || (statistic[statistic.length - 1] == statistic[statistic.length - 2])) {
            icon = "ui-icon ui-icon-arrowthick-2-e-w";
        } else
        if (statistic[statistic.length - 1] > statistic[statistic.length - 2]) {
            icon = "ui-icon ui-icon-arrowthick-1-ne";
        } else
        if (statistic[statistic.length - 1] < statistic[statistic.length - 2]) {
            icon = "ui-icon ui-icon-arrowthick-1-se";
        }
        var trend = $(`<span class="trend ui-icon ${icon}"></span><span class="trend ui-widget ui-corner-all"  title="${title}">${text}</span>`);
        $( `#tr${whichid} .trend`).remove();
        $( `#tr${whichid}` ).append(trend);
    }
}

function sync_with_server(callinit) {
    // try to synchronize with server
    $.ajaxSetup({timeout: 5000});
    var jqxhr = $.post( "http://" + location.hostname + ":8080/json/",
        JSON.stringify(g_storage),
        null, "json")
    .done(function(data) {
        localStorage.setItem(localStorageKey, JSON.stringify(data));
        console.log( "data synced" );
        show_sync(true);
        if (callinit) init();
    })
    .fail(function() {
        show_sync(false);
        console.log( "data not synced" );
        if (callinit) init();
    })
    .always(function() {
        console.log( "complete" );
    });
}

function show_sync(synced) {
    // show sync hint
    $( "#sync" ).removeClass("hidden");
    $( "#sync" ).show();
    $("#synctext").text((synced ? "S" : "Not s") + "ynchronized with server");
    $("#sync").fadeOut(4000, function() {
        $(this).addClass("hidden");
    });
}
