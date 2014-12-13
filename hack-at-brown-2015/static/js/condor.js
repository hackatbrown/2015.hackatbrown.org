(function ($) {
    $.fn.condor = function (options) {
        var settings = $.extend({
                maxInputs: 10,
                uniqueNames: true,
                namePrefix: 'inputs',
                inactiveHint: 'add input',
                activeHint: '',
                activeIcon: 'linkify',
                addCallback: function() {},
                activateCallback: function() {},
                inputType: 'text'
            }, options),
            target = this,
            numInputs = 0;

        function addField(hint, parentclass, childclass) {
            target.append("<div class='field " + parentclass + " '><div class='ui left icon input " + childclass + "'><input type='" + settings.inputType + "' placeholder='" + settings.inactiveHint + "'><i class='plus icon'></i></div></div>");
        }

        function makeActive(field) {
            var index = numInputs,
                name = settings.namePrefix + '-' + index,
                input = $(".condor-add input");
            numInputs += 1;
            $(".condor-add > div").removeClass('inverted');
            $(".condor-add i").removeClass('plus');
            $(".condor-add i").addClass(settings.activeIcon);
            input.attr('placeholder', settings.activeHint);
            if (settings.uniqueNames) {
                input.attr('name', name);
            } else {
                input.attr('name', settings.namePrefix);
            }
            $(field).unbind();
            $(input).unbind();
            $(field).removeClass('condor-add');

            //Bind a thing that detects when the field gets filled
            input.bind("propertychange keyup input paste", function (event) {
                // If no longer an empty string
                if ($(this).val() !== '') {
                    input.unbind("propertychange keyup input paste blur");
                    if (numInputs < settings.maxInputs) {
                        addInactiveField(numInputs);
                    }

                    input.blur(function () {
                        if (($(this).val() === '') && (numInputs > 1)) {
                            $(this).unbind();
                            $(this).parent().parent().remove();
                            numInputs -= 1;
                        }
                    });
                }
            });
            
            input.blur(function () {
                if (($(this).val() === '') && (numInputs > 1)) {
                    $(this).unbind();
                    $(this).parent().parent().remove();
                    numInputs -= 1;
                    
                    if (numInputs < settings.maxInputs) {
                        addInactiveField(numInputs);
                    }
                }
            });

            settings.activateCallback.call();
        }

        function addInactiveField(id) {
            addField('add another link', 'condor-add', 'inverted');
            var field = $(".condor-add"),
                input = $(".condor-add input");
            $(input).click(function () {
                $(this).unbind("click");
                $(input).unbind("focusin");
                makeActive(this);
            });
            $(input).focusin(function () {
                $(this).unbind("focusin");
                $(field).unbind("click");
                makeActive(field);
            });
            settings.addCallback.call();
            return field;
        }

        addInactiveField(numInputs);
        makeActive($(".condor-add"));
    }

}(jQuery));