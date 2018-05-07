var testdata = [
    ['d1_0', 'e1', 0, '',  '10'],
    ['d2_1', 'e2', 0, '',  '20'],
    ['d3_0', 'e3', 0, 'a', '30'],
    ['d4_1', 'e4', 0, '',  '40'],
    ['d5_0', 'e5', 0, 'b', '50'],
    ['d6_2', 'e6', 0, 'ab','60'],
    ['d7_1', 'e7', 0, '',  '70'],
    ['d8_2', 'e8', 0, 'b', '85'],
    ['d9_2', 'e9', 0, 'a', '90']
];

var catlookup = {
    'a': 'Adj',
    'b': 'Adv',
    'v': 'Verb',
    's': 'Subst',
    'p' : 'Präp'
};

var st = {
    selection: [],
    showlevel: 0,
    showcat: '',
    showpos: 0,
    showde: true,
    randomarray: [],
    randommode: false,
    pos: 0,
    data: [],
    showpopup: false,
};

var spt = {
    getselection: function(s) {
        /* s.showcat is string with all selected themes
           s.showsrc is string with all selected sources
           First push each element to selection if it matched one of themes
           Next delete every element from selection which doesn't match sources
         */
        s.selection = []
        s.data.forEach(function(element, index, array) {
            if (element[2] >= s.showlevel) {
                outer_loop:
                for (var ti = 0; ti < s.showcat.length; ti++) {
                    var themecharacter = s.showcat.charAt(ti);
                    for (var si = 0; si < s.showsrc.length; si++) {
                        var srccharacter = s.showsrc.charAt(si);
                        if ((element[3].indexOf(themecharacter) != -1)
                            && (element[3].indexOf(srccharacter) != -1)) {
                            s.selection.push(index);
                            break outer_loop;
                        }
                    }
                }
            }
        });
        this.clearranomarray(s);
        return s.selection.length;
    },

    getrandomarray: function (s) {
        s.randomarray = [];
        s.selection.forEach(function(element) {
            s.randomarray.push(element);
        });
        if (s.randommode) {
            var n = s.selection.length - 1;
            for (var i = 0; i < 10; i++) {
                var index1 = Math.floor((1 + n) * Math.random());
                var index2 = Math.floor((1 + n) * Math.random());
                var temp = s.randomarray[index1];
                s.randomarray[index1] = s.randomarray[index2];
                s.randomarray[index2] = temp;
            }
        }
    },

    clearranomarray: function (s) {
        s.randomarray = s.randomarray.filter(function(element) {
            return s.selection.indexOf(element) != -1;
        });
    },

    eventclass:  {
        next: 10,
        prev: 11,
        toggle: 12,
        level0: 0,
        level1: 1,
        level2: 2,
        show0: 100,
        show1: 101,
        show2: 102,
        random: 200,
        slide: 300,
    },

    main: function (s, event) {
        switch (event) {
            case this.eventclass.next:
                s.pos += 1;
                if (s.pos >= s.selection.length) {
                    s.pos = 0;
                }
                break;
            case this.eventclass.prev:
                s.pos -= 1;
                if (s.pos < 0) {
                    s.pos = s.selection.length - 1;
                }
                break;
            case this.eventclass.toggle:
                s.showde = !s.showde;
                break;
            case this.eventclass.level0:
            case this.eventclass.level1:
            case this.eventclass.level2:
                s.data[s.randomarray[s.pos]][2] = event;
                if (this.getselection(s) == 0) {
                    s.showlevel = 0;
                    this.getselection(s);
                    this.getrandomarray(s);
                    s.pos = 0;
                }
                break;
            case this.eventclass.show0:
            case this.eventclass.show1:
            case this.eventclass.show2:
                s.showlevel = event - 100;
                if (this.getselection(s) == 0) {
                    s.showpopup = true;
                    s.showlevel = 0;
                    this.getselection(s);
                }
                this.getrandomarray(s);
                s.pos = 0;
                break;
            case this.eventclass.random:
                s.randommode = !s.randommode;
                this.getrandomarray(s);
                break;
            case this.eventclass.slide:
                var value = $("#sliderpage").val();
                var max = $("#sliderpage").attr("max");
                var min = $("#sliderpage").attr("min");
                /*console.log(value, max, min, s.selection.length);*/
                s.pos = parseInt((s.selection.length - 1) * (value - min) / (max - min));
                break;
            default: /* event variable contains themestr */
                s.showcat = event.t;
                s.showsrc = event.s;
                /* FIXME */
                if (this.getselection(s) == 0) {
                    s.showpopup = true;
                    s.showcat = st.allcat;
                    s.showsrc = st.allsrc;
                    this.getselection(s);
                }
                this.getrandomarray(s);
                s.pos = 0;
                break;
        }
        if (typeof exports == 'undefined') {
            this.update(s);
        }
    },

    update: function (s) {
        if (s.pos >= s.randomarray.length) {
            s.pos = 0;
        }
        if (typeof window.localStorage !== "undefined") {
            localStorage.setItem("pos_es", JSON.stringify(s.pos));
        }
        s.showpos = s.randomarray[s.pos];
        if (s.showde == true) {
            $("#words").html(s.data[s.showpos][0]);
            $("#words").removeClass('bgspain').addClass('bggerman');
        } else {
            $("#words").html(s.data[s.showpos][1]);
            $("#words").removeClass('bggerman').addClass('bgspain');
        }
        $('#cnt').text("[" + (s.pos + 1) + "/" + s.selection.length + "]");

        var cat = [];
        for (var i = 0; i < s.data[s.showpos][3].length; i++) {
            var ch = s.data[s.showpos][3][i];
            if (typeof catlookup[ch] != 'undefined') {
                cat.push(catlookup[ch]);
            }
        }
        $('#cat').text(cat.join('/'));

        for (var i = 0; i < 3; ++i) {
            $("#radio-choice-" + i).attr("checked", data[s.showpos][2] == i).checkboxradio("refresh");
        }
        $("#sliderpage").attr("max", s.selection.length);
        $("#sliderpage").attr("min", 1);
        $("#sliderpage").val(s.pos + 1).slider("refresh");
    },


    loaddata: function (s) {
        if ($(location).attr('hash') == "#clear") {
          console.log('localStorage cleared');
          localStorage.clear();
        }
        if (typeof window.localStorage !== "undefined") {
            /* Code for localStorage/sessionStorage. */
            console.log('Local storage available');
            var fontsize = localStorage.getItem("fontsize");
            var hashv = {};
            if (fontsize != null) {
                fontsize = JSON.parse(fontsize);
                console.log("fontsize", fontsize);
                $("#event *").css({
                    "font-size": fontsize
                });
            }
            var pos = localStorage.getItem("pos_es");
            if (pos != null) {
                s.pos = JSON.parse(pos);
            }
            console.log("s.pos:" + s.pos);
            s.sourcestr = localStorage.getItem("sourcestr");
            if (s.sourcestr == null) s.sourcestr = "";
            s.themestr = localStorage.getItem("themestr");
            if (s.themestr == null) s.themestr = "";
            console.log(s);
            var group = localStorage.getItem("group_es");
            if (group == null) {
                /* init group */
                group = {};
                for (var i = 0; i < s.data.length; ++i) {
                    /* each element of group is identified by s.data[i][4] (adler32) and storesthe group */
                    group[s.data[i][4]] = s.data[i][2]
                }
                localStorage.setItem("group_es", JSON.stringify(group));
            } else {
                group = JSON.parse(group);
                for (var i = 0; i < s.data.length; ++i) {
                    hashv[s.data[i][4]] = 1;
                    if (s.data[i][4] in group) {
                        s.data[i][2] = group[s.data[i][4]]
                    }
                }
                /* cleanup group by removing all items not data */
                var delindex = [];
                var key;
                for (key in group) {
                    if (!(key in hashv)) {
                        delindex.push(key);
                    }
                }
                for (var i = 0; i < delindex.length; ++i) {
                    console.log(delindex[i]);
                    delete group[delindex[i]];
                }
                localStorage.setItem("group_es", JSON.stringify(group));
            }
        } else {
            console.log('No local storage');
        }
    },
}

function show_statistic() {
    var s = {};
    st.data.forEach(function(element) {
        for (var c of element[3]) {
            s[c] = typeof s[c] == "undefined" ? 1 : s[c] + 1 ;
        }
    });
    $("<p> Letzte Änderung " + lastmodified + "</p>").appendTo("#statistic > div:nth-child(2)");
    themestr.forEach(function(element) {
        $("<p id='st" + element[0] + "'>" + s[element[0]] + ' ' + element[1] + "</p>").appendTo("#statistic > div:nth-child(2)")
    });
}

function popup() {
    function changetitle(widget, title) {
        var w = $(widget + " option:first")
        var savetitle = w.text();
        w.text(title)
        $(widget).selectmenu("refresh", true);
        return savetitle;
    }
    st._ = $("#words").html();
    var _ = $("#theme option:first").text();
    $("#words").html("<span style='font-size:200%; font-weight:bold'>Auswahl leer!</span>");
    var _tsource = changetitle("#source", "Auswahl leer!");
    var _ttheme = changetitle("#theme", "Auswahl leer!");
    $("#words")
        .animate(
            {opacity: "toggle"},
            700)
        .animate(
            {opacity: "toggle"},
            700,
            function() {
                spt.update(st);
                changetitle("#source", _tsource);
                changetitle("#theme", _ttheme);
            });
    st.showpopup = false;
}

function onmenuchange() {
    /* Callback function for theme and source menu */
    var themestr = "";
    $("#theme option:selected").each(function() {
        themestr += $(this).val();
    });
    var sourcestr = "";
    $("#source option:selected").each(function() {
        sourcestr += $(this).val();
    });
    localStorage.setItem("sourcestr", sourcestr);
    localStorage.setItem("themestr", themestr);

    spt.main(st, {'t': themestr, 's': sourcestr});
    // console.log('settheme', themestr, st.showpopup);
    if (st.showpopup) {
        popup();
        $("#theme option").each(function() {
            if (st.lastcat.indexOf($(this).val()) != -1) {
                $(this).attr("selected", "selected");
            }
        });
        $("#source option").each(function() {
            if (st.lastsrc.indexOf($(this).val()) != -1) {
                $(this).attr("selected", "selected");
            }
        });
        $("#theme").selectmenu("refresh", true);
        $("#source").selectmenu("refresh", true);
    } else {
        st.lastsrc = sourcestr;
        st.lastcat = themestr;
    }
}


function pageinit(event, eventdata) {
    $("#sliderform").on("slidestop", function( event, ui ) {
        spt.main(st, spt.eventclass.slide);
    } );
    $("#theme option").prop("selected", false);
    $("#event").on("swipeleft", function() {
        spt.main(st, spt.eventclass.next);
    });
    $("#event").on("swiperight", function() {
        spt.main(st, spt.eventclass.prev);
    });
    $("#next").on("click", function() {
        spt.main(st, spt.eventclass.next);
    });
    $("#prev").on("click", function() {
        spt.main(st, spt.eventclass.prev);
    });
    $("#toggle").on("click", function() {
        spt.main(st, spt.eventclass.toggle);
    });

    $("#event").on("tap", function() {
        spt.main(st, spt.eventclass.toggle);
    });
    $("#slider").on("change", function() {
        spt.main(st, spt.eventclass.random);
    });

    $('#theme').on('change', onmenuchange);
    $('#source').on('change', onmenuchange);

    $("[name=radio-choice-level]").on("click", function() {
        var level = parseInt($("input[name='radio-choice-level']:checked").val());
        spt.main(st, level);
        console.log('setlevel', level);
        if (typeof window.localStorage !== "undefined") {
            var group = JSON.parse(localStorage.getItem("group_es"));
            group[st.data[st.randomarray[st.pos]][4]] = level;
            localStorage.setItem("group_es", JSON.stringify(group));
        }
    });
    $("[name=radio-view-level]").on("click", function() {
        var level = parseInt($("input[name='radio-view-level']:checked").val());
        spt.main(st, level + 100);
        console.log('showlevel', level);
        if (st.showpopup) {
            popup();
            $("#radio-view-0").attr("checked", true).checkboxradio("refresh");
            $("#radio-view-1").attr("checked", false).checkboxradio("refresh");
            $("#radio-view-2").attr("checked", false).checkboxradio("refresh");
        }
    });
    $("#event").addClass('ui-corner-all');
    $("#font-size").on("change", function() {
        $("#event *").css({
            "font-size": $(this).val()
        });
        if (typeof window.localStorage !== "undefined") {
            localStorage.setItem("fontsize", JSON.stringify($(this).val()));
        }
    });

    st.data = data;
    spt.loaddata(st);
    console.log(st.sourcestr, st.themestr);

    var flag;

    var select = $("select#theme");
    st.allcat = '';
    flag = false;
    themestr.forEach(function(element, index, array) {
        if ((st.themestr.indexOf(element[0]) != -1) || ((index >= array.length - 1) && (flag == false))) {
            select.append("<option selected='selected' value='" + element[0] + "'>" + element[1] + "</option>")
            st.allcat += element[0];
            flag = true;
        } else {
            select.append("<option value='" + element[0] + "'>" + element[1] + "</option>");
        }
    });
    select.selectmenu();
    select.selectmenu('refresh', true);
    st.showcat = st.allcat;
    st.lastcat = st.allcat;

    var source = $("select#source");
    st.allsrc = '';
    flag = false;
    sourcestr.forEach(function(element, index, array) {
        if ((st.sourcestr.indexOf(element[0]) != -1) || ((index >= array.length - 1) && (flag == false))) {
            source.append("<option selected='selected' value='" + element[0] + "'>" + element[1] + "</option>");
            st.allsrc += element[0];
            flag = true;
        } else {
            source.append("<option value='" + element[0] + "'>" + element[1] + "</option>");
        }
    });
    source.selectmenu('refresh', true);
    source.selectmenu();
    st.showsrc = st.allsrc;
    st.lastsrc = st.allsrc;


    spt.getselection(st);
    spt.getrandomarray(st);
    spt.update(st);

    $("#sliderpage").attr("max", st.selection.length);
    $("#sliderpage").attr("min", 1);
    $("#sliderpage").val(st.pos).slider("refresh");

    show_statistic();
}
