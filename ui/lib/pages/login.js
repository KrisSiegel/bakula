/*
    ./lib/pages/login.js

    This is the controller for the login.html web page
*/
var pages = pages || { };
pages.login = (function () {
    "using strict";

    jQuery(document).ready(function () {

        var elements = {
            loginForm: jQuery("#loginForm"),
            inputs: {
                username: jQuery("#username"),
                password: jQuery("#password")
            }
        };

        var validateText = function (input) {
            var valid = true;
            var val = input.val();
            if (val.trim().length === 0) {
                valid = false;
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
        };

        elements.inputs.username.on("change", function (e) {
            validateText(elements.inputs.username);
        });

        elements.inputs.password.on("change", function (e) {
            validateText(elements.inputs.password);
        });

        elements.loginForm.submit(function (event) {
            event.preventDefault();

            var username = elements.inputs.username.val();
            var password = elements.inputs.password.val();

            var errorMessage = "The following issues must be corrected before submission:\n\n";;
            var errorCount = 0;
            for (var field in elements.inputs) {
                if (elements.inputs.hasOwnProperty(field)) {
                    if (!elements.inputs[field].parent().hasClass("has-success")) {
                        if (elements.inputs[field].parent().hasClass("has-error")) {
                            errorCount++;
                            errorMessage = errorMessage + " - The " + elements.inputs[field].attr("displayName") + " field has an invalid value.\n";
                        } else {
                            errorCount++;
                            errorMessage = errorMessage + " - The " + elements.inputs[field].attr("displayName") + " field is empty.\n";
                        }
                    }
                }
            }

            if (errorCount > 0) {
                alert(errorMessage);
            } else {
                bodata.bakula.login(username, password, function (err, result) {
                    if (err != null) {
                        return alert("Login failed");
                    }

                    sessionStorage.setItem("credentials", username);
                    location.href = "/";
                });
            }
        });
    });
}());
