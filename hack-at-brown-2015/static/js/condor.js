// CONDOR 1.5 Made by Chen Ye, MIT License

(function ($) {

    $.fn.condor = function (command) {
        var settings,
            $target = $(this),
            numInputs = 0,
            publicMethods = {
                getValues: function () {
                    var values = [],
                        i = 0;
                    $target.find(".condor-active input").each(function () {
                        if (this.value.length !== 0) {
                            values[i] = this.value;
                            i += 1;
                        }
                    });
                    return values;
                }
            };


        function refreshNumInputs() {
            numInputs = $target.children(".condor-active").length;
            return numInputs;
        }

        function addField(hint, parentclass, childclass) {
            $target.append("<div class='field " + parentclass + " '><div class='ui left icon input " + childclass + "'><input type='" + settings.inputType + "' placeholder='" + settings.inactiveHint + "'><i class='plus icon'></i></div></div>");
        }

        function addActiveField(id) {
            addField('', 'condor-active', '');
            return $target.children(".condor-active").filter(function () {
                return $(this).find("input").val().length === 0;
            }).first();
        }

        function addInactiveField(id) {
            var $field = $target.children(".condor-add");
            addField('add another link', 'condor-add', settings.inactiveInputClass);
            settings.addCallback.call();
            return $field;
        }
        
        function conditionalAddInactiveField() {
            if ($target.hasClass("no-new")) {
                $target.removeClass("no-new");
                refreshNumInputs();
                if (numInputs < settings.maxInputs) {
                    addInactiveField(numInputs);
                }
            }
        }

        function removeInactiveFields() {
            $target.children(".condor-add").remove();
        }

        function bindInactive() {
            $target.on("click focusin", ".condor-add", function () {
                makeActive($(this));
            });
        }

        function bindActive() {
            //This instantaneously detects if an active input gets filled
            $target.on("propertychange keyup input paste", ".condor-active", function (event) {
                var $this = $(this),
                    $input = $this.find("input");
                
                // If no longer an empty string
                if ($input.val() === '') {
                    $target.addClass("no-new");
                    removeInactiveFields();
                } else {
                    conditionalAddInactiveField();
                }
            });

            $target.on("blur", ".condor-active input", function (event) {
                if ((this.value === '') && (numInputs > settings.minInputs)) {
                    $(this).parent().parent().remove();
                    numInputs -= 1;
                    conditionalAddInactiveField();
                }                
            });

        }

        function makeActive($field) {
            var index,
                name,
                $input = $field.find('input'),
                $icon = $field.find('i.icon');
            numInputs += 1;
            $field.find('.input').removeClass(settings.inactiveInputClass);
            $icon.removeClass('plus');
            $icon.addClass(settings.activeIcon);
            $input.attr('placeholder', settings.activeHint);
            if (settings.uniqueNames) {
                index = refreshNumInputs();
                name = settings.namePrefix + '-' + index;
                $input.attr('name', name);
            } else {
                $input.attr('name', settings.namePrefix);
            }
            $field.addClass('condor-active');
            $field.removeClass('condor-add');
            $target.addClass('no-new');
            settings.activateCallback.call();
        }

        if (publicMethods[command]) {
            return publicMethods[command].apply(this, []);
        } else {
            settings = $.extend({
                minInputs: 1,
                maxInputs: 10,
                namePrefix: 'inputs',
                uniqueNames: true,
                inactiveHint: 'add input',
                inactiveInputClass: 'inverted',
                activeHint: '',
                activeIcon: 'linkify',
                addCallback: function () {},
                activateCallback: function () {},
                inputType: 'text',
                prepopulate: []
            }, command);
        }

        function prepopulate() {
            settings.prepopulate.forEach(function (value, index, ar) {
                var $field = addActiveField(refreshNumInputs()),
                    $input = $field.find("input");
                $input.val(value);
                makeActive($field);
            });
        }

        function initialize() {
            $target.addClass('no-new');
            bindActive();
            bindInactive();
            prepopulate();
            for (i = numInputs; i < settings.minInputs; i++) {
                addInactiveField(numInputs);
            }
            makeActive($target.children(".condor-add"));
        }

        initialize();
        return this;
    };

}(jQuery));