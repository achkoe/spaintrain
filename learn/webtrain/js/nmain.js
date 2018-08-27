var g_storage;
const localStorageKey = "nwebtrain";
const NEW = "new";


$(document).ready(function() {
    var elem, toc, select, item_id;

    // initialize local storage if not already done
    if (!localStorage.getItem(localStorageKey)) {
        localStorage.setItem(localStorageKey, JSON.stringify({}));
    }
    g_storage = JSON.parse(localStorage.getItem(localStorageKey));

    // set up table of contents
    toc = $("<div/>", {id:"toc", class:"rtable"});
    for (var header in ld) {
        item_id = parseInt(header);
        if (!g_storage[item_id]) {
            g_storage[item_id] = {};
        }
        var lessondata = g_storage[item_id];
        var sessionlist = Object.keys(lessondata);
        sessionlist = sessionlist.sort().reverse();

        select = $("<select id='s" + item_id + "'/>")
        select.append( $("<option>" + NEW + "</option>"))
        for (var i = 0; i < sessionlist.length; i++) {
            select.append( $("<option>" + (i + 1) + " - " + sessionlist[i] + "</option>"))
        }
        toc.append($("<div/>", {class:"rtablerow"})
            .append(
                $("<div/>", {class:"rtablecell"}).append($("<a>", {html:header, href:"#", onclick:"show_lesson('" + item_id + "', '" + header + "')"})),
                $("<div/>", {class:"rtablecell"}).append(select)
        ));
    }
    $("body").append(toc);
    // set up upper and lower toolbar
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
});




function show_lesson(item_id, lessonname) {
    //console.log(lessonname);
    var re = new RegExp("\\[([^\\]]+)\\]", "g");
    var taskindex = 0;
    // clear current session
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
            //console.log(matches);
            var solutionlist = new Array();
            var replacement = ""
            var pos = 0;
            var name;
            var taskclass = "taskns"
            for (var matchindex = 0; matchindex < matches.length; matchindex++) {
                taskclass = "task";
                replacement += item.slice(pos, matches[matchindex]["index"])
                pos = matches[matchindex]["index"];
                name = '' + parseInt(lessonname) + '_' + taskindex + '_' + matchindex;
                if (matches[matchindex][1].startsWith(":")) {
                    var enumitemlist = matches[matchindex][1].slice(2).split('|');
                    //console.log(enumitemlist);
                    replacement += "<span class='rbtask cbradio'>"
                    for (var enumindex = 0; enumindex < enumitemlist.length; enumindex++) {
                        var id = name + '_' + enumindex;
                        if (enumitemlist[enumindex].startsWith('!')) {
                            enumitemlist[enumindex] = enumitemlist[enumindex].slice(1);
                            solutionlist.push(enumitemlist[enumindex]);
                        }
                        replacement += '<input required="required" type="radio" id="' + id + '" name="' + name + '"/><label for="' + id + '">'
                                    + enumitemlist[enumindex] + '</label>'
                    }
                    replacement += "</span>"
                    //<input required="required" type="radio" id="1_10_0_1" name="1_10_0"/><label for="1_10_0_1">feminin</label></span></p>
                } else {
                    replacement += '<input required="required" type="text" id="' + name + '" name="' + name + '" size="' + matches[matchindex][1].length + '"/>'
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
                    .append($("<div/>",  {class:"slider", id:"s_" + item_id + "_" + taskindex}), $("<div/>", {class:"column", html: solutionlist.join(', ')})));
            }
            $("#session").append(container.append(column));
            taskindex += 1;
        }
    }
    $( ".cbradio input" ).checkboxradio({icon: false});
        $(".slider").each(function(index) {
        $( this ).slider({range: "min", max: 2, value: 0});
        $( this ).find(".ui-slider-handle").attr("tabindex", index + 1);
    });
    $("#toc").hide();
    $(".show").removeClass( "ui-icon-circle-close" );
    $(".show").addClass( "ui-icon-lightbulb" );
    $("#session .solution").hide();
}

function show_solution() {
    $(".show").toggleClass("ui-icon-lightbulb");
    $(".show").toggleClass("ui-icon-circle-close");
    $("#session .solution").toggle();
}
