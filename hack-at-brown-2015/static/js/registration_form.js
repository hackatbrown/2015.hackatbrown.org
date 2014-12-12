
    function addNag(msg, parent) {
        var nags = parent.children(".nag");
        if (nags.length == 0)
            parent.append("<div class='nag'>" + msg + "</div>");
        else {
            parent.removeClass("valid");
            parent.children().removeClass("valid");
        }
    }

    function validateForm() {
        var validated = true;

        // Check if name is filled out
        if (!$("input[name='name']").val()) {
            $("input[name='name']").addClass("invalid");
            addNag("We're gonna need your name.", $("input[name='name']").parent());
            validated = false;
            console.log("Invalid name");
        }

        // Check if email is filled out
        if (!validateEmail($(".field input[name='email']").val())) {
            $(".field input[name='email']").addClass("invalid");
            addNag("Please enter a valid email address.", $(".field input[name='email']").parent());
            validated = false;
            console.log("Invalid email");
        }


        // Check if school is filled out
        if (!$("input[name='school']").val()) {
            $("input[name='school']").addClass("invalid");
            addNag("Please enter your school.", $("input[name='school']").parent());
            validated = false;
            console.log("Invalid school");
        }

        if (!$("select[name='year']").val()) {
            $(".select2-container.drop").addClass("invalid");
            addNag("Please choose your current year.", $("select[name='year']").parent());
            validated = false;
            console.log("Invalid year");
        }

        var shirt_valid = true;

        // Check if they filled out shirt gender & size
        if (!$("input[name='shirt_gen']:checked").val()) {
            shirt_valid = false;
            validated = false;
            console.log("Invalid shirt gender");
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
        if($mates) {
            $mates = $mates.split(",");
            var validEmails = true;
            $.each($mates, function(index, email) {
                if (!validateEmail(email)) {
                    validEmails = false;
                }
            });

            if (!validEmails) {
                console.log("Invalid teammate email(s)");
                addNag("Please make sure all your teammates' emails are valid.", $("#teammates").parent());
            } else {
                $("#teammates").addClass("valid");
            }
        } else {
            $("#teammates").addClass("valid");
        }

        // Check if they filled out hardware hack
        if (!$("input[name='hardware_hack']:checked").val()) {
            addNag("Please indicate whether you're interested in hardware hacking.", $("label[for='hardware_hack']").parent());
            validated = false;
            console.log("Invalid hardware hack");
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


    $(document).ready(function () {
        H5F.setup(document.getElementById("registration_form"), {
            onSubmit: function (e) {
                e.preventDefault();
                if (validateForm()) {
                    $("#registration_form input[type=submit]").val("Registering you...").attr({
                        disabled: true
                    });
                    console.log("POSTing response");
                    $("#registration_form").ajaxSubmit({
                        success: function (response) {
                            //$('#submit_button').removeAttr('disabled');
                            response = JSON.parse(response)
                            if (response.success === true) {
                                console.log("displaying splash page")
                                $(".splash .double_right").html(response.replace_splash_with_html);
                                window.location.hash = "";
                            } else{
                                $("#registration_form input[type=submit]").val("Email already Registered!").attr({
                                    disabled: false
                                });
                            }
                    return false;
                    }});
                    } else {
                        $(".errorsPresent").addClass("nag");
                        $('html,body').animate({scrollTop: 0}, 1000);
                    }
            }
        });


        /* Validation Styling */
        function toggleInvalid(el, email) {
            var validEmail = true;

            if (email) {
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
            if($("input[name='shirt_gen']:checked").val())
                $("div.shirt_size").addClass("valid");
        });

            // Check for hardware hack validation
        $("input[type='radio'][name='hardware_hack'] + label").click(function () {
            $("table[for='hardware_hack'").addClass("valid");
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

        /* Condor dynamic link input stuff */
        $(".condor").condor({
            uniqueNames: false,
            namePrefix: 'links',
            activeHint: 'Github, Dribbble, Behance, etc.',
            inactiveHint: 'add another link',
            addCallback: fixSplashHeight,
        });
        
        //select2 dropdown
        $("#source").select2({
            width: "100%",
            minimumResultsForSearch: -1,
            placeholder: "Select Year",
        });
        
        $("#source").on("change", function() {
            $("select[name='year']").addClass("valid");
            $(".select2-container.drop").removeClass("invalid");
            $(".select2-container.drop").addClass("valid");
        });
        
        $("#teammates").select2({
            width: "100%",
            tags:[""],
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
                var $inputs = $("input[type=text], input[type=email], input[type=radio], input[type=checkbox]");
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


