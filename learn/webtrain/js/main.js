$(document).ready(function(){
    /* Hier der jQuery-Code */
    init();
});


var g_lesson;

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
            "onclick": "show_lesson('d" + item_id + "')",
        });
        var select = $("<select id='s" + item_id + "'/>")
        select.append( $("<option>new</option>", {value: 0}))
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
    $("#" + g_lesson).hide();
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
    $("#toc").hide();
    $("#" + lesson).show();
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
    $("#" + g_lesson + " .solution").toggle();
}