$(document).ready(function() {
    console.log("start");
    var toc = $( "<div/>" , {id:"toc", class:"rtable"});
    for (var header in ld) {
        toc.append($("<div/>", {class:"rtablerow"})
            .append($("<div/>", {class:"rtablecell"})
                .append($("<a>", {html:header, href:"#", onclick:"show_lesson('l" + parseInt(header) + "')"}))));
    }
    $( "body" ).append(toc);
});

function show_lesson(which) {
    console.log(which);
}