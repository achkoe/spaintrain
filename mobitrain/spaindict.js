var sdt = {
    tsearch: function (a, b) {
        return a.search(new RegExp(b, "i")) != -1
    },

    nsearch: function (a, b) {
        return a == b;
    },

    lsearch: function (langarray, what) {
        searchindex = typeof what == "number" ? 1 : 0;
        searchfun = [this.tsearch, this.nsearch][searchindex]
            //console.log(searchfun);
        for (var i = 0; i < langarray.length; i++) {
            if (searchfun(langarray[i][searchindex], what)) {
                return i;
            }
        }
        return -1;
    },

    submit: function (langarray, langstr) {
        /* Execute search */
        var pos = this.lsearch(langarray, $("#search" + langstr).attr("value"));
        if (pos >= 0) {
            var index = langarray[pos][1]
            $("#searches").attr("value", es[this.lsearch(es, index)][0]);
            $("#searchde").attr("value", de[this.lsearch(de, index)][0]);
            $.each($("#table td"), function(index, value) {
                /*console.log(value);*/
                $(value).removeClass("highlight");
            });
            $("#" + langstr + index).addClass("highlight");
        }
    }
}

function pageinit(event, eventdata) {
    function dataLoaded(data) {
        $.each(de, function(index, value) {
            // set datalist options for de lang
            var option;
            var td, tr, img, span;

            option = document.createElement("option");
            option.setAttribute('value', value[0]);
            $("#langde").append(option);

            // set datalist options for es lang
            option = document.createElement("option");
            option.setAttribute('value', es[index][0]);
            $("#langes").append(option);

            // populate table
            tr = document.createElement("tr")
            $("#tcontent").append(tr);
            // language de
            $(tr).append( $("<td id='de" + value[1] + "' class='right'>&nbsp;" + value[0] + "&nbsp;<img src='germany.png' height='10pt'/></td>") );
            // language es
            var pos = sdt.lsearch(es, value[1])
            $(tr).append( $("<td id='es" + es[pos][1] + "'><img src='spain.png' height='10pt'/>&nbsp;" + es[pos][0] + "</td>") );
        });
        
        $("#table").tablesorter({
            headers: {
                0: { sorter: 'german' },
                1: { sorter: 'spain' }
            }
        });
        $("#lefthead").addClass("lefthead");
    }

    dataLoaded();

    $("#formde").submit(function(event) {
        sdt.submit(de, "de");
        event.preventDefault();
    });
    $("#formes").submit(function(event) {
        sdt.submit(es, "es");
        event.preventDefault();
    });

    // add parser through the tablesorter addParser method 
    $.tablesorter.addParser({
        // set a unique id 
        id: 'spain',
        is: function(s) {
            // return false so this parser is not auto detected 
            return false;
        },
        format: function(s) {
            // format your data for normalization 
            return s.toLowerCase().replace(/^a\s/, "").replace("á", "a").replace("é", "e").replace("ó", "o").replace("í", "i").replace("ú", "u").replace("ñ", "n");
        },
        // set type, either numeric or text 
        type: 'text'
    });

    // add parser through the tablesorter addParser method 
    $.tablesorter.addParser({
        // set a unique id 
        id: 'german',
        is: function(s) {
            // return false so this parser is not auto detected 
            return false;
        },
        format: function(s) {
            // format your data for normalization 
            return s.toLowerCase().replace(/^zu\s/, "").replace("ä", "a").replace("ö", "e").replace("ü", "o").replace("ß", "s");
        },
        // set type, either numeric or text 
        type: 'text'
    });
}
