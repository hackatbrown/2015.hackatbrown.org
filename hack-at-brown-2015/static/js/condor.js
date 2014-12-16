(function ($) {
  
    $.fn.condor = function (command) {
        var settings,
            target = this,
            numInputs = 0,
            publicMethods = {
                getValues: function () {
                    console.log("getting values");
                    var values = [], i = 0;
                    $(target).find(".condor-active input").each(function () {
                        if (this.value.length !== 0) {
                            values[i] = this.value;
                            i += 1;
                        }
                    });
                    return values;
                }
            };
        
        
        function refreshNumInputs() {
            numInputs = $(target).children(".condor-active").length;
            return numInputs;
        }

        function addField(hint, parentclass, childclass) {
            target.append("<div class='field " + parentclass + " '><div class='ui left icon input " + childclass + "'><input type='" + settings.inputType + "' placeholder='" + settings.inactiveHint + "'><i class='plus icon'></i></div></div>");
        }

        function makeActive(field) {
            var index,
                name,
                input = $(field).find('input'),
                icon =  $(field).find('i.icon');
            numInputs += 1;
            $(field).find('.input.inverted').removeClass('inverted');
            $(icon).removeClass('plus');
            $(icon).addClass(settings.activeIcon);
            input.attr('placeholder', settings.activeHint);
            if (settings.uniqueNames) {
                index = refreshNumInputs();
                name = settings.namePrefix + '-' + index;
                input.attr('name', name);
            } else {
                input.attr('name', settings.namePrefix);
            }
            $(field).unbind();
            $(input).unbind();
            $(field).addClass('condor-active');
            $(field).removeClass('condor-add');

            //Bind a thing that detects when the field gets filled
            input.bind("propertychange keyup input paste", function (event) {
                // If no longer an empty string
                if (this.value !== '') {
                    input.unbind("propertychange keyup input paste blur");
                    refreshNumInputs();
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
        
        function prepopulate() {
            settings.prepopulate.forEach(function (value, index, ar) {
                var field = addActiveField(refreshNumInputs()),
                    input = $(field).find("input");
                $(input).val(value);
                makeActive(field);
                $(input).unbind();
            });
        }
                                         
        function addActiveField(id) {
            addField('', 'condor-active', '');
            return $(target).children(".condor-active").filter(function () { return $(this).find("input").val().length === 0; }).first();
        }

        function addInactiveField(id) {
            addField('add another link', 'condor-add', 'inverted');
            var field = $(target).find(".condor-add"),
                input = $(field).find("input");
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
        
        if (publicMethods[command]) {
            return publicMethods[command].apply(this, []);
        } else {
            settings = $.extend({
                maxInputs: 10,
                uniqueNames: true,
                namePrefix: 'inputs',
                inactiveHint: 'add input',
                activeHint: '',
                activeIcon: 'linkify',
                addCallback: function () {},
                activateCallback: function () {},
                inputType: 'text',
                prepopulate: []
            }, command);
        }
        
        prepopulate();
        addInactiveField(numInputs);
        makeActive($(target).children(".condor-add"));
        return this;
    };

}(jQuery));