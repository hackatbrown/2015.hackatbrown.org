$(document).ready(function() {
    console.log("parsing");
    var uniList = $(".institution");
    var result = new Array(uniList.length);
    for(var i = 0; i < uniList.length; i++) {
        var uni = $(uniList[i]);
        var domain = uni.attr("href");
        domain = domain.substring(11, domain.length - 1);
        var name = uni.text();
        
        var item = {
            "label": name,
            "domain": domain
        };

        result[i] = item;
    }

    console.log(result);
    var csvContent = "data:text/csv;charset=utf-8,";

    $("body").empty();
    $("body").text(JSON.stringify(result));

});