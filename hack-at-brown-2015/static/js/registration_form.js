    function fieldInvalid(fieldName) {
        var $element;
        var msg;
        switch (fieldName) {
            case 'email':
                msg = "Please enter a valid email address.";
                console.log("Invalid email");
                break;
            case 'name':
                msg = "Please enter your full name";
                console.log("Invalid name");
                break;
            case 'school':
                msg = "Please enter your school";
                console.log("Invalid school");
                break;
            case 'year':
                $element = $("select[name='year']");
                msg = "Please choose your current year.";
                console.log("Invalid year");
                $(".select2-container.drop").addClass("invalid");
                break;
            case 'shirt_size':
                msg = "Please choose a complete shirt size.";
                $element = $("div.shirt_size");
                break;
            case 'teammates':
                msg = "Please make sure all your teammates' emails are valid.";
                $element = $("#teammates");
                console.log("Invalid teammate email(s)");
                break;
            case 'hardware_hack':
                msg = "Please indicate whether youre interested in hardware hacking.";
                $element = $("label[for='hardware_hack']");
                console.log("Invalid hardware hack");
                break;
            case 'first_hackathon':
                msg = "Please indicate if this will be your first hackathon.";
                $element = $("label[for='first_hackathon']");
                console.log("Invalid first hackathon");
                break;
            case 'agree':
                msg = "You must agree to the Code of Conduct before registering."
                $element = $("#agree");
                console.log("Invalid agree");
                break;
            default:
                break;
        }

        if (!$element) {
            $element = $("input[name='" + fieldName + "']");
        }

        $element.addClass("invalid");
        addNag(msg, $element.parent());

    }


    function validateForm() {
        var validated = true;

        // Check if name is filled out
        if (!$("input[name='name']").val()) {
            fieldInvalid('name');
            validated = false;
        }

        // Check if email is filled out
        if (!validateEmail($(".field input[name='email']").val())) {
            fieldInvalid('email');
            validated = false;
        }

    if (!$("select[name='year']").val()) {
        $(".select2-container.drop").addClass("invalid");
        addNag("Please choose your current year.", $("select[name='year']").parent());
        validated = false;
        console.log("Invalid year");
    }

        // Check if school is filled out
        if (!$("input[name='school']").val()) {
            fieldInvalid('school');
            validated = false;
        }

        if (!$("select[name='year']").val()) {
            fieldInvalid('year');
            validated = false;
        }

    if (!$("input[name='shirt_size']:checked").val()) {
        shirt_valid = false;
        validated = false;
        console.log("Invalid shirt size");
    }

    if (!shirt_valid) {
        addNag("Please choose a complete shirt size.", $("div.shirt_size").parent());
    }

    // Check for valid teammate emails
    var $mates = $("#teammates").val();
    if ($mates) {
        $mates = $mates.split(",");
        var validEmails = true;
        $.each($mates, function (index, email) {
            if (!validateEmail(email)) {
                validEmails = false;
            }
        });

        if (!shirt_valid) {
            fieldInvalid('shirt_size');
        }

        // Check for valid teammate emails
        var $mates = $("#teammates").val();
        if($mates) {
            $mates = $mates.split(",");
            var validEmails = true;
            $.each($mates, function(index, email) {
                if (!validateEmail(email)) {
                    validEmails = false;
                }
            });

            if (!validEmails) {
                fieldInvalid('teammates');
            } else {
                $("#teammates").addClass("valid");
            }
        } else {
            $("#teammates").addClass("valid");
        }
    } else {
        $("#teammates").addClass("valid");
    }

        // Check if they filled out hardware hack
        if (!$("input[name='hardware_hack']:checked").val()) {
            fieldInvalid('hardware_hack');
            validated = false;
        }

        // Check if they filled out first time question
        if (!$("input[name='first_hackathon']:checked").val()) {
            fieldInvalid('first_hackathon');
            validated = false;
        }

    /* // Check for resume
        if (!$(".resume-upload").val()) {
            addNag("Upload your resume, man/woman/being/dog/mythical creature.", $(".resume-upload").parent());
            validated = false;
            console.log("Invalid resume");
        }*/

    // Check if they agree to the Code of Conduct
    if (!$("#agree").prop('checked')) {
        addNag("You must agree to the Code of Conduct before registering.", $("#agree").parent());
        validated = false;
        console.log("Invalid agree");
    }

    return validated;
}

//fun icon matching stuff
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
    };
    for (domain in recognizedDomains) {
        if (url.indexOf(domain) > -1) {
            console.log("matched with " + domain);
            console.log(uiIcon);
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
    }
    $(condorObject).on("change", ".condor-active > .input > input", detectedChange);
}


    $(document).ready(function () {
        H5F.setup(document.getElementById("registration_form"), {
            onSubmit: function (e) {
                e.preventDefault();
                if (validateForm()) {
                    $("#registration_form input[type=submit]").val("Registering you...").attr({
                        disabled: true
                    });
                    $("#registration_form").ajaxSubmit({
                        success: function (response) {
                            //$('#submit_button').removeAttr('disabled');
                            response = JSON.parse(response)
                            if (response.success === true) {
                                $(".splash .double_right").html(response.replace_splash_with_html);
                                window.location.hash = "";
                            } else {
                                indicateFailure();
                                if (response.msg) {
                                    $("#registration_form input[type=submit]").val(response.msg).attr({
                                            disabled: false
                                        });
                                }
                                if (response.field) {
                                    fieldInvalid(response.field);
                                }
                                //We need a new blobstore url for each time we submit the form.
                                if (response.newURL) {
                                    $('#registration_form').get(0).setAttribute('action', response.newURL);
                                }

                            }
                    return false;
                    }});
                    } else {
                        indicateFailure();
                    }
            }
        });

        function indicateFailure() {
            $(".errorsPresent").addClass("nag");
            $('html,body').animate({scrollTop: 0}, 1000);
        }


        /* Validation Styling */
        function toggleInvalid(el, isEmail) {
            var validEmail = true;

        if (isEmail) {
            validEmail = validateEmail(el.val());
        }

        if (el.val() == "" || !validEmail) {
            el.addClass("invalid");
            el.removeClass("valid");
        } else {
            el.removeClass("invalid");
            el.addClass("valid");
        }
    }

    $(".registration_form input[name='name']").focusout(function () {
        toggleInvalid($(this), false);
    });

    $(".registration_form input[name='email']").focusout(function () {
        toggleInvalid($(this), true);
    });

    $(".registration_form input[name='school']").focusout(function () {
        toggleInvalid($(this), false);
    });

    // Check for shirt size validation
    $(".shirt_size input[type='radio'][name='shirt_gen'] + label").click(function () {
        if ($("input[name='shirt_size']:checked").val())
            $("div.shirt_size").addClass("valid");
    });

    $(".shirt_size input[type='radio'][name='shirt_size'] + label").click(function () {
        if ($("input[name='shirt_gen']:checked").val())
            $("div.shirt_size").addClass("valid");
    });

        // Check for hardware hack validation
        $("input[type='radio'][name='hardware_hack'] + label").click(function () {
            $("table[for='hardware_hack'").addClass("valid");
        });

        // Check for first hackathon validation
        $("input[type='radio'][name='first_hackathon'] + label").click(function () {
            $("table[for='first_hackathon'").addClass("valid");
        });

            // Check for file upload
        $("input[type='file']").change(function () {
            $(this).addClass("valid");
        });

            // Check for agreement with CoC
        $("input[type='checkbox'][name='agree']").click(function () {
            $("label[for='agree']").addClass("valid");
        });

        var $universities = [];
        $.getJSON("/static/data/universities.json", function (data) {
            $.each(data, function (key, val) {
                $universities[key] = val;
            })
        });

        // Attach resume upload button with actual file input & style
        $("#resume-over").click(function () {
            $("#resume").click();
        });
        $("#resume").change(function() {
            if ($("#resume").val()) {
                var $parsed_val = $("#resume").val().split("\\");
                $(".file-name").html($parsed_val[$parsed_val.length - 1]);
                $(".resume-button").addClass("on");
            } else {
                $(".file-name").html("No file chosen.");
                $(".resume-button").removeClass("on");
            }
        });


        /* On email change & valid, check for university domain */
        function searchUniversities(domain) {
            $universities.forEach(function (obj) {
                if (domain == obj["domain"]) {
                    $(".registration_form input[name='school']").val(obj["label"]);
                    $(".registration_form input[name='school']").removeClass("invalid");
                }
            });
        }

        $("input[type='email']").change(function () {
            var splitEmail = $(this).val().split('@');
            if (splitEmail.length == 2) {
                var univ = searchUniversities(splitEmail[1]);
                if (univ != null)
                    $(".registration_form input.schools").val(univ);
            }
        });

        /* Autocomplete suggestions for schools */
        $(function () {
            $(".schools").autocomplete({
                source: $universities
            });
        });

        });

    /* Condor dynamic link input stuff */
    var linkRepeater = $(".condor").condor({
        uniqueNames: false,
        namePrefix: 'links',
        activeHint: 'Github, Dribbble, Behance, etc.',
        inactiveHint: 'add another link',
        addCallback: fixSplashHeight,
        inputType: 'url',
    });
    
    trackCondor(linkRepeater);

    //select2 dropdown
    $("#source").select2({
        width: "100%",
        minimumResultsForSearch: -1,
        placeholder: "Select Year",
    });

    $("#source").on("change", function () {
        $("select[name='year']").addClass("valid");
        $(".select2-container.drop").removeClass("invalid");
        $(".select2-container.drop").addClass("valid");

        if ($(this).val() == "highschool") {
            $(".hs-warning").show();
        } else {
            $(".hs-warning").hide();
        }
    });

    $("#teammates").select2({
        width: "100%",
        tags: [""],
        tokenSeparators: [",", " "],
        dropdownCssClass: "select2-drop-override",
        maximumSelectionSize: 3
    });

    var $dRestrictions = ["Vegetarian", "Vegan", "Gluten Free", "Kosher", "Lactose Intolerant", "Nuts Allergy", "Treenuts Allergy", "Soy Allergy",
"Shellfish Allergy", "Corn Allergy", "No Pork", "No Ham", "No Beef", "No Mutton", "Halal", "No Red Meat", "None"];

    $("#diet").select2({
        width: "100%",
        tags: $dRestrictions,
        tokenSeparators: [","],
        dropdownCssClass: "bigdrop"
    });

    //        $("#teammates").on("select2-opening", function(e) {
    //            e.preventDefault();
    //        });



    /* Prevent horizontal scrolling of element into view on focus */
    $(document).on('keydown', ':focus', function (event) {
        if ((event.keyCode || event.which) == 9) {
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
    });


})