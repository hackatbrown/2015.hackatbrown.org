// The MIT License (MIT)

// Copyright (c) 2014 Glass Umbrella. Created by Eddie Lee.

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

(function($) {
    $.fn.gutabslider = function(options) {

        var mainClassName = "gu-tab-slider";
        var barClassName = "gu-sliding-bar";

        var positionTabUnderCurrentActiveTab = function($element) {
            var $activeTab = $element.find("li.active a");
            if (_.any($activeTab)) {
                positionTabUnderline($element, $activeTab);
            }
        };

        var positionTabUnderline = function($element, $tab) {
            var $slidingBar = $element.find("." + barClassName);
            //Set left
            var left = $tab.position().left;
            $slidingBar.css("left", left + "px");

            //Set top
            var tabHeight = $tab.outerHeight();
            var top = $tab.position().top;
            $slidingBar.css("top", (top + tabHeight) + "px");

            //Set width
            var width = $tab.outerWidth();
            $slidingBar.css("width", width + "px");
        }

        return this.each(function(index, element) {
            $element = $(element);

            //Don't reapply
            if ($element.hasClass(mainClassName)) {
                if (options === "active-tab-changed") {
                    positionTabUnderCurrentActiveTab($element);
                }

                return true;
            }

            //Add sliding bar
            $element.append("<span class='" + barClassName + "'></span>");
            var $slidingBar = $element.find("." + barClassName);
            $slidingBar.css("position", "absolute");
            $slidingBar.css("display", "block");
            $slidingBar.css("width", "0");
            $slidingBar.css("height", "3px");

            //Position tab under currently active tab
            positionTabUnderCurrentActiveTab($element);

            //Resize when window size changes
            $(window).resize(_.debounce(function() {
                positionTabUnderCurrentActiveTab($element);
            }, 100));

            //Finished
            $element.addClass(mainClassName);
        });
    };
})(jQuery);