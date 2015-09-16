/*
    ./lib/pages/common.js

    This is a set of common functions for pages
*/
var pages = pages || { };
pages.common = (function () {
    "using strict";

    jQuery(document).ready(function () {

        var elements = {
            usernameBtn: jQuery("#usernameBtn")
        };

        if (sessionStorage) {
            if (sessionStorage.getItem("credentials") == null && location.href.indexOf("login.html") === -1) {
                // Not logged in; redirect if not on login page.
                window.location = "/login.html";
            } else if (location.href.indexOf("login.html") !== -1) {
                // Login page
            } else {
                // Authorized; display username!
                elements.usernameBtn.text(sessionStorage.getItem("credentials"));
            }
        }
    });

    return {
        validateText: function (input, allowedCharacters) {
            var valid = true;
            var val = input.val();
            if (val.trim().length === 0) {
                valid = false;
            } else if (allowedCharacters !== undefined) {
                if (val.length > 0) {
                    for (var i = 0; i < val.length; ++i) {
                        if (allowedCharacters.indexOf(val.charAt(i)) === -1) {
                            valid = false;
                            break;
                        }
                    }
                }
            }

            if (valid) {
                input.parent().addClass("has-success");
                input.parent().removeClass("has-error");
            } else {
                if (val == "") {
                    input.parent().removeClass("has-success");
                    input.parent().removeClass("has-error");
                } else {
                    input.parent().removeClass("has-success");
                    input.parent().addClass("has-error");
                }
            }
        }
    };
}());
