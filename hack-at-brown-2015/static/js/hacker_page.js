//    Navigation
function setTabActive(tab) {
    $(".top-bar_li").removeClass("active");
    $(tab).addClass("active");
}

function switchPanes(paneNumber) {
    var $panes = $(".panes");
    $panes.removeClass("in-pane0 in-pane1");
    $panes.addClass("in-pane" + paneNumber);
    $(".pane" + paneNumber).addClass("active");
}

function switchToMyInfo() {
    switchPanes(1);
}

function switchFromMyInfo() {
    switchPanes(0);
}

function initalizeHamburger() {
    // Hamburger menu for mobile
    $("nav ul > li a").click(function () {
        $("nav").removeClass("open");
    });
    $(".hamburger").click(function () {
        $("nav").toggleClass("open");
    });
}

function confirmDeleteHacker(secret) {
    console.log(secret);
    if (window.confirm("Are you sure you want to cancel your registration?")) {
        window.location.href = "/__delete_hacker/" + secret;
    }
}

// Resume Upload

function requestNewUploadURL() {
    $.ajax({
        type: 'GET',
        url: '/secret/__newurl/' + secret,
        success: function (response) {
            response = JSON.parse(response);
            newResumeURL = response.newURL;
        }
    });
}

function updateResume(value, uiinput, secret, responseStatus) {

    var $button = $(uiinput).find(".ui.button"),
        $buttonText = $button.children("span"),
        width = $button.outerWidth(),
        complete = false;

    function resetState(e) {
        $button.removeClass("complete");
        $button.removeAttr('style');
        $button.addClass('fadeBackground');
        $buttonText.fadeOut(200, function () {
            $buttonText.text("Re-upload");
            $buttonText.fadeIn(200);
        });
        $button.unbind('mouseenter', resetState);
        setTimeout(function() {
            $button.removeClass('fadeBackground');
        }, 1000);
    }

    //Set the button state to loading
    $button.addClass("loading active");

    var data = new FormData();
    data.append("resume", $('.resume-upload')[0].files[0]);

    $.ajax({
        xhr: function () {
            var xhr = new window.XMLHttpRequest();
            //Upload progress
            xhr.upload.addEventListener("progress", _.throttle(function (evt) {
                if (evt.lengthComputable && !complete) {
                    var percentComplete = evt.loaded / evt.total;
                    $button.css("box-shadow", "inset " + (width * percentComplete) + 5 + "px 0 0 -1px #1b8eb9");
                }
            }, 1000), false);
            return xhr;
        },
        url: newResumeURL,
        data: data,
        cache: false,
        contentType: false,
        processData: false,
        type: 'POST',
        success: function (response) {
            complete = true;
            $button.css("box-shadow", "inset " + width + 5 + "px 0 0 -1px #26a59f");
            $button.addClass("complete");
            $button.removeClass("loading active");
            $buttonText.text("Complete!");
            response = JSON.parse(response);
            $resumeView = $('.view-resume');

            $newLink = $("<a class='view-resume'></a>");
            $newLink[0].innerHTML = response.fileName;
            $newLink.attr({
                'href' : response.downloadLink,
                'download' : response.fileName,
                'target' : '_blank'
            });
            $resumeView.replaceWith($newLink);

            $button.one('mouseenter', resetState);
            setTimeout(resetState, 2500);
        },
        failure: function (response) {
            console.log("I have failed youuuu");
        }
    });
}

function slideOut($element) {
    $element.stop().hide().slideToggle(200);

}

function slideIn($element) {
    $element.stop().show().slideToggle(200);
}


//  Form processing out

function saveChange(key, value, uiinput, secret, responseStatus) {
    if (key === 'resume') {
        updateResume(value, uiinput, secret, responseStatus);
        requestNewUploadURL();
    }

    var data = {},
        $icon = $(uiinput).children(".icon"),
        oldIcon = $icon.attr('class');
    data[key] = value;
    $(uiinput).addClass('loading');
    $.ajax({
        url: '/__update_hacker/' + secret,
        type: 'POST',
        data: JSON.stringify(data),
        success: function (data, status) {
            $(uiinput).removeClass('loading');
            if (responseStatus) {
                $(uiinput).addClass('fade');
                $icon.attr('class', "checkmark icon");
                setTimeout(function () {
                    $(uiinput).removeClass('fade');
                    if ((oldIcon !== "checkmark icon") || (oldIcon !== "remove icon")) {
                        $icon.attr('class', oldIcon);
                    }
                }, 1500);
            }
        },
        failure: function (data, status) {
            $(uiinput).removeClass('loading');
            if (responseStatus) {
                $(uiinput).addClass('error fade');
                $icon.className = "remove icon";
                setTimeout(function () {
                    $(uiinput).removeClass('fade');
                    if ((oldIcon !== "remove icon") || (oldIcon !== "remove icon")) {
                        $icon.attr('class', oldIcon);
                    }
                }, 1500);
            }
        }
    });
}

function trim1(str) {
    return str.replace(/^\s\s*/, '').replace(/\s\s*$/, '');
}

function domainMatch(uiIcon, url) {
    var recognizedDomains = {
            'dribbble.com': "dribbble",
            'facebook.com': "facebook",
            'linkedin.com': "linkedin",
            'github.com': "github",
            'jsfiddle.net': "jsfiddle",
            'behance.net': "behance",
            'soundcloud.com': "soundcloud",
            'deviantart.com': "deviantart"
        },
        domain;
    for (domain in recognizedDomains) {
        if (url.indexOf(domain) > -1) {
            //            console.log("matched with " + domain);
            $(uiIcon).attr('class', "icon " + recognizedDomains[domain]);
            return;
        }
    }
    $(uiIcon).attr('class', "icon linkify");
}

function trackCondor(condorObject) {
    var detectedChange = function () {
        var icon = $(this).siblings(".icon"),
            links = condorObject.condor("getValues");
        this.value = this.value.trim().replace(/^.*?:\/\//, "");
        domainMatch(icon, this.value);
        saveChange("links", links.toString(), $(condorObject).find(".condor-active > .input"), secret, false);
    };
    $(condorObject).on("change", ".condor-active > .input > input", detectedChange);
}

//  Form processing in

function processCSV(csvString) {
    return csvString.split(',');
}

function populateDefaultRadio(key, value) {
    $('input:radio[name=' + key + '][value=' + value + ']').attr('checked', true);
}

/* Prevent horizontal scrolling of element into view on focus */
//$(document).on('keydown', ':focus', function (event) {
//    if ((event.keyCode || event.which) === 9) {
//        //TODO: Generalize and support selecting other kinds of input
//      var $inputs = $("input[type=text], input[type=url], input[type=email], input[type=radio], input[type=checkbox], input[type=button]"),
//            index = $inputs.index(this),
//            $next;
//        // Index previous or next input based on the shift key
//        index += event.shiftKey ? -1 : 1;
//        // If we are in the range of valid inputs (else browser takes focus)
//        if (index >= 0 && index < $inputs.length) {
//            $next = $inputs.eq(index);
//            event.preventDefault();
//            //console.log($next);
//            $next.focus();
//            return false;
//        }
//    }
//
//    if ((event.keyCode || event.which) === 13) {
//        $("input").blur();
//    }
//});
