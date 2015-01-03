//    Navigation
function initalizeNavMenu(selector) {
    setTimeout(function () {
        $(selector).gutabslider();
    }, 800);
}

function setTabActive(tab) {
    $(".top-bar_li").removeClass("active");
    $(tab).addClass("active");
    setTimeout("$('.top-bar_ul').gutabslider('active-tab-changed')", 100);
}

function switchPanes(paneNumber) {
    var $panes = $(".panes");
    $panes.removeClass("in-pane0 in-pane1 in-pane2");
    $panes.addClass("in-pane" + paneNumber);
    $(".pane" + paneNumber).addClass("active");
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

// Messages
var $message_container = $(".message_container");
function messagesCheckNone() {
    if ($(".message").length == 0) {
        $message_container.html("<h3 class='secondary'>None!</h3>");
    }
}
// File Upload

function deleteFile(uiInput, key) {
    var blobKey = $(uiInput).find('a').attr('href').split('__serve/')[1];


    var data = {'key' : key, 'blobKey' : blobKey};
    $.ajax({
        type: 'POST',
        data: data,
        url: '/secret/__delete_file/' + secret,
        success : function() {
            $(uiInput).remove();
        }
    });
}

function confirmDeleteHacker(secret) {
    $('#delete-modal')
      .modal({
        selector : {
            approve  : '.yes',
            deny     : '.no',
        },
        onApprove : function() {
            window.location.href = "/__delete_hacker/" + secret;
        }
      })
      .modal('show');
}

function rsvp(secret) {
    $('#rsvp-modal')
      .modal({
        selector : {
            approve  : '.yes',
            deny     : '.no',
        },
        onApprove : function() {
            $.ajax({
                type: 'POST',
                url: '/secret/__rsvp/' + secret,
                success: function (response) {
                    response = JSON.parse(response);
                    if (response.success) {
                        $status = $('.admit_status');
                        var $statusText = $status.children("span");
                        $status.removeClass('accepted');
                        $status.addClass('confirmed');
                        $statusText.fadeOut(200, function () {
                            $statusText.text("confirmed");
                            $statusText.fadeIn(200);
                        });
                        $('.rsvp.field').fadeOut(200, function () {
                            this.remove();
                        });

                        $('#rsvp-link').remove();
                        $('#receipts-upload').show();

                    }
                }
            });
        }
      })
      .modal('show');
}

// Resume Upload
function uploadResume(uiinput) {
    //This is a 2-part process - first we get a new blobstore URL
    //We pass in the update function as a callback.
    //We call the callback function with the new URL as an argument
    //Then we submit a multipart form request to that URL.
    //There's a handler in hackerFile.py which will receive it.
    requestNewUploadURL(uiinput, 'resume');
}

function toggleReimbursementForm(on) {
    $form = $('#address_form');
    $inputs = $form.find('div:not(.upload) :input')
    if (on) {
        slideOut($form, 1000);
        $inputs.removeAttr('disabled');
    } else {
        $inputs.attr('disabled', 'disabled');
    }
}

function uploadReceipts(uiinput) {
    var callback = function() {toggleReimbursementForm(true);};
    requestNewUploadURL(uiinput, 'receipts', callback, true);
}

function requestNewUploadURL(uiinput, key, callback, multiple) {
    $.ajax({
        type: 'GET',
        url: '/secret/__newurl/' + secret + '/' + key,
        success: function (response) {
            response = JSON.parse(response);
            var newFileURL = response.newURL;
            updateFile(newFileURL, uiinput, key, callback, multiple);
        }
    });
}

function createFileView(key, multiple) {
    $item = $('<div class="view-' + key + '"><a href="dummy">dummy</a></div>');

    if (multiple) {
        $icon = $('<i class="ui basic rsvp button delete-file">Delete</i>');
        $icon.click(function() {
            deleteFile(this.parentNode, key);
        });
        $item.append($icon);
    }
    return $item;

}

function updateFile(newFileURL, uiinput, key, callback, multiple) {
    multiple = multiple || false;

    $uiInput = $(uiinput);
    var $button = $uiInput.find("." + key + "-upload");
    var $buttonText = $button.children("span");
    var width = $button.outerWidth();
    var complete = false;

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
    var i =0;
    files = $button.filter("input")[0].files;
    for (index in files) {
        data.append(key, files[index]);
    }

    data.append('multiple', multiple)


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
        url: newFileURL,
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
            $lastItem = $('.view-' + key).last();
            if (!multiple || $lastItem.length === 0 || $lastItem.is('span')) {
                $lastItem.remove();
            }
            for(var i = 0; i < response.downloadLinks.length; i++) {
                $newItem = createFileView(key, multiple);
                $newLink = $newItem.find('a');
                $newLink[0].innerHTML = response.fileNames[i];
                $newLink.attr({
                    'href' : response.downloadLinks[i],
                    'download' : response.fileNames[i],
                    'target' : '_blank'
                });
                $uiInput.append($newItem);
            }

            $button.on('mouseenter', resetState);
            setTimeout(resetState, 2500);

            setTimeout(callback, 1000);
        },
        failure: function (response) {
            console.log("I have failed youuuu");
        }
    });
}

function slideOut($element, time) {
    time = time || 200;
    $element.stop().hide().slideToggle(time);
}

function slideIn($element) {
    $element.stop().show().slideToggle(200);
}

//  Form processing out

function saveChange(key, value, uiinput, secret, responseStatus) {
    if (key === 'resume') {
        if (value) {
            uploadResume($(".resume-upload.upload.ui.button").parent());
        }
        return;
    } else if (key == 'email') {
        return;
    }
    console.log(key, value);

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
