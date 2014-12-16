$(document).ready(function () {

    var $signUpForUpdatesForm = $("#sign-up-for-updates");
    $signUpForUpdatesForm.submit(function (e) {
        e.preventDefault();
        $signUpForUpdatesForm.addClass('loading');
        $.ajax({
            url: $signUpForUpdatesForm.attr('action'),
            data: $signUpForUpdatesForm.serialize(),
            method: 'POST',
            success: function () {
                $signUpForUpdatesForm.removeClass('loading').addClass('signed-up');
                $signUpForUpdatesForm.find('input[type=email]').attr('placeholder', "we'll keep you posted")
            }
        })
        $signUpForUpdatesForm.find('input[type=email]').blur().val("");
    })
    $signUpForUpdatesForm.find('input[type=email]').focus(function () {
        $(this).attr('placeholder', 'email@school.edu');
    }).blur(function () {
        $(this).attr('placeholder', 'subscribe for updates');
    })
});


// Navigation thingus

function sectionChanged(s) {
    setTimeout("$('.top-bar_ul').gutabslider('active-tab-changed')", 10);
}

function transferInitInfo() {
    var vals = $("form.init_reg").serializeArray();
    $(".registration_form input[name='email']").val(vals[0].value);
}

function fixSplashHeight() {
    var height = 0;
    var splash = document.getElementById("hero");
    var panels = document.getElementById("panels");
    if (splash.classList.contains("reg")) {
        height = (Math.ceil(splash.offsetHeight / 60) * 60) - 840;
    }
    $(".panels").css("transform", "translate3d(0," + height + "px, 0)");
    $("#skrollr-body").css("padding-bottom", (height) + "px");
}


function initalizeNavMenu(selector) {
    $(selector).onePageNav({
        currentClass: "active",
        changeHash: false,
        begin: sectionChanged,
        scrollChange: sectionChanged,
        filter: ':not(.secondary)',
    });

    setTimeout(function () {
        $(selector).gutabslider();
    }, 400);
}

// Function that validates email address through a regular expression.
function validateEmail(sEmail) {
    var filter = /^([\w\!\#$\%\&\'\*\+\-\/\=\?\^\`{\|\}\~]+\.)*[\w\!\#$\%\&\'\*\+\-\/\=\?\^\`{\|\}\~]+@((((([a-z0-9]{1}[a-z0-9\-]{0,62}[a-z0-9]{1})|[a-z])\.)+[a-z]{2,6})|(\d{1,3}\.){3}\d{1,3}(\:\d{1,5})?)$/i;
    if (filter.test(sEmail)) {
        return true;
    } else {
        return false;
    }
}

// Function to add validation nags to input
function addNag(msg, parent) {
    console.log("nag added");
    var nags = parent.children(".nag");
    if (nags.length == 0) {
        parent.append("<div class='nag'>" + msg + "</div>");
        parent.removeClass("valid");
        parent.children().removeClass("valid");
    }
    else {
        $(nags).text(msg);
        parent.removeClass("valid");
        parent.children().removeClass("valid");
    }
}

/* From Modernizr */
function whichTransitionEvent(){
    var t;
    var el = document.createElement('fakeelement');
    var transitions = {
//      fuck vendor prefixes!
      'transition':'transitionend',
      'OTransition':'oTransitionEnd',
      'MozTransition':'transitionend',
      'WebkitTransition':'webkitTransitionEnd'
    }

    for(t in transitions){
        if( el.style[t] !== undefined ){
            return transitions[t];
        }
    }
  
    return null;
}

function transitionToForm() {
    $(".registration_form").addClass("active");
  
    $('html,body').animate({scrollTop: 0}, 1000);
    
    $(".splash, .cancel_reg").addClass("reg translated");
    $(".top-bar_li#hello_top a").fadeOut(500, function () {
        $(this).text("Registration");
        setTimeout("$('.top-bar_ul').gutabslider('active-tab-changed')", 100);
        $(this).fadeIn(800);
    });
  
    fixSplashHeight();
    var transitionEvent = whichTransitionEvent();
    console.log(transitionEvent);
    setTimeout("document.getElementById('name').focus();", 900);
}

function transitionFromForm() {
    var transitionEvent = whichTransitionEvent();
  
    $('html,body').animate({scrollTop: 0}, 1000);
    $(".splash").removeClass("reg translated");
  
    $(".top-bar_li#hello_top a").fadeOut(500, function () {
        $(this).text("Hello");
        setTimeout("$('.top-bar_ul').gutabslider('active-tab-changed')", 100);
        $(this).fadeIn(800);
    });
  
    fixSplashHeight();
  
//    setTimeout("$('.registration_form').removeClass('active')", 2000);
}

function initalizeReg() {
    // Add event handlers for inital registration toggle
    $("form.init_reg").submit(function (e) {
        e.preventDefault();

        // Validate
        if (!validateEmail($(".init_reg input[type='email']").val())) {
            addNag("Please enter a valid email address.", $(".init_reg input[type='email']").parent());
            console.log("Splash Page: Invalid email!");
            return;
        } else {
            $(".init_reg .init_submit").addClass("valid");
            var registered = false;
            $("#registration_email").ajaxSubmit({
                async: false,
                success: function (response) {
                    //$('#submit_button').removeAttr('disabled');
                    response = JSON.parse(response)
                    if (response.registered === true) {
                        console.log("you already registered!");
                        addNag("You've already registered!", $(".init_reg input[type='email']").parent());
                        registered = true;
                        return;
                    }
                }
            });
            if (!registered) {
                transitionToForm();
                transferInitInfo();
            }
        }

    });

    $(".cancel_reg").click(function() { 
      $(this).fadeOut(200, function () {
            $(this).removeClass("reg");
            $(this).fadeIn(0);
      });
      transitionFromForm();
    });
}

function initalizeHamburger() {
    // Hamburger menu for mobile
    $("nav ul > li a").click(function () {
        $("nav").removeClass("open");
    })
    $(".hamburger").click(function () {
        $("nav").toggleClass("open");
    });
}

$(document).ready(function () {
    var iOS = /(iPad|iPhone|iPod)/g.test(navigator.userAgent),
        $fader = $(".fader");

    setTimeout(function() {
        $($fader).remove();
    }, 2200);
    
    // P-P-P- 
    if (!iOS) {
        skrollr.init({
            mobileCheck: function () {
                return false;
            },
            forceHeight: false,
        })
    }

    // Fix splash height if the browser resizes
    $(window).resize(function () {
        fixSplashHeight();
    });

    initalizeReg();

    initalizeHamburger();

    initalizeNavMenu('.top-bar_ul');
  
    // Make sure splash height is good on doc ready
    fixSplashHeight();
    
    $($fader).addClass("inactive");
    
    setTimeout(function() {
        $($fader).remove();
    }, 500);

});