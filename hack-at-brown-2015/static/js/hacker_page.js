//    Navigation
function setTabActive(tab) {
    $(".top-bar_li").removeClass("active");
    $(tab).addClass("active");
}

function switchPanes(paneNumber) {
    var $panes = $(".panes");
    $($panes).removeClass("in-pane0 in-pane1");
    $($panes).addClass("in-pane"+paneNumber);
    $(".pane"+paneNumber).addClass("active");
}

function switchToMyInfo() {
    switchPanes(1);
}

function switchFromMyInfo() {
    switchPanes(0);
}

function saveChange(key, value, uiinput, secret) {
    console.log("key: " + key + " value: " + value);
    var data = {};
    data[key] = value;
    $(uiinput).addClass('loading');
    $.ajax({
      url : '/__update_hacker/' + secret,
      type : 'POST',
      data : JSON.stringify(data),
      success : function(data, status) {
          $(uiinput).removeClass('loading');
          $(uiinput).children("i").addClass('checkmark fade');
          setTimeout(function() {$(uiinput).children("i").removeClass('checkmark fade')}, 2000)
      },
      failure : function(data, status) {
          
      }
    });
}

function populateDefaultRadio(key, value) {
    $('input:radio[name='+key+'][value='+value+']').attr('checked', true);
}

/* Prevent horizontal scrolling of element into view on focus */
$(document).on('keydown', ':focus', function (event) {
    if ((event.keyCode || event.which) === 9) {
        //TODO: Generalize and support selecting other kinds of input
        var $inputs = $("input[type=text], input[type=url], input[type=email], input[type=radio], input[type=checkbox]");
        //                console.log($inputs);
        var index = $inputs.index(this);
        // Index previous or next input based on the shift key
        index += event.shiftKey ? -1 : 1;
        // If we are in the range of valid inputs (else browser takes focus)
        if (index >= 0 && index < $inputs.length) {
            var $next = $inputs.eq(index);
            event.preventDefault();
            // Move, not scroll, to the next/prev item....
            //                    MoveIntoView($next);
            //console.log($next);
            $next.focus();
            return false;
        }
    }
    
    if ((event.keyCode || event.which) == 13) {
        $("input").blur();
    }
});