$(document).ready(function() {
    var elem;
    var toc = $("<div/>", {id:"toc", class:"rtable"});
    for (var header in ld) {
        toc.append($("<div/>", {class:"rtablerow"})
            .append($("<div/>", {class:"rtablecell"})
                .append($("<a>", {html:header, href:"#", onclick:"show_lesson('" + header + "')"}))));
    }
    $("body").append(toc);
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




function show_lesson(which) {
    //console.log(which);
    $("#session").empty();
    var re = new RegExp("\\[([^\\]]+)\\]", "g");
    for (var header in ld[which]) {
        $("#session").append($("<h1/>", {html:header}));
        for (var index in ld[which][header]) {
            var item = ld[which][header][index];
            var matches = new Array();
            while ((match = re.exec(item)) !== null) {
                matches.push(match);
            }
            //console.log(matches);
            var solution = new Array();
            var replacement = ""
            var pos = 0;
            var name;
            for (var i = 0; i < matches.length; i++) {
                replacement += item.slice(pos, matches[i]["index"])
                pos = matches[i]["index"];
                name = '' + parseInt(which) + '_' + index + '_' + i;
                if (matches[i][1].startsWith(":")) {
                    var enumitemlist = matches[i][1].slice(2).split('|');
                    console.log(enumitemlist);
                    replacement += "<span class='rbtask cbradio'>"
                    for (var j = 0; j < enumitemlist.length; j++) {
                        var id = name + '_' + j;
                        replacement += '<input required="required" type="radio" id="' + id + '" name="' + name + '"/><label for="' + id + '">'
                                    + enumitemlist[j].slice(enumitemlist[j].startsWith('!') ? 1 : 0) + '</label>'
                    }
                    replacement += "</span>"
                    //<input required="required" type="radio" id="1_10_0_1" name="1_10_0"/><label for="1_10_0_1">feminin</label></span></p>
                } else {
                    replacement += '<input required="required" type="text" id="' + name + '" name="' + name + '" size="' + matches[i][1].length + '"/>'
                }
                pos += matches[i][0].length;
            }
            //console.log(item);
            //console.log(pos);
            replacement += item.slice(pos);
            $("#session").append($("<p/>", {class:"task", html:replacement}));
            $( ".cbradio input" ).checkboxradio({icon: false});
        }
    }
    $("#toc").hide();
}