/*
    ./lib/pages/events.js

    This is the controller for the events.html web page
*/
var pages = pages || { };
pages.events = (function () {
    "using strict";

    jQuery(document).ready(function () {

        var elements = {
            dropZone: jQuery("#json"),
            eventForm: jQuery("#eventForm"),
            inputs: {
                key: jQuery("#eventKey"),
                type: jQuery("#eventType"),
                json: jQuery("#json")
            }
        };

        var validInput = "abcdefghijklmnopqrstuvwxyz_.0123456789";
        var validateTextArea = function (input) {
            var valid = true;
            var val = input.val();
            try {
                JSON.parse(val);
                valid = true;
            } catch (ex) {
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

        var resetForm = function (e) {
            if (e === undefined) {
                // Manually called
                elements.eventForm[0].reset();
            }

            for (var field in elements.inputs) {
                if (elements.inputs.hasOwnProperty(field)) {
                    elements.inputs[field].parent().removeClass("has-success");
                    elements.inputs[field].parent().removeClass("has-error");
                }
            }
        };

        elements.eventForm.on("reset", resetForm);

        elements.inputs.key.on("change", function (e) {
            pages.common.validateText(elements.inputs.key, validInput);
        });

        elements.inputs.type.on("change", function (e) {
            pages.common.validateText(elements.inputs.type, validInput);
        });

        elements.inputs.json.on("change", function (e) {
            validateTextArea(elements.inputs.json);
        });

        elements.dropZone[0].addEventListener("dragenter", function (e) {
            e.stopPropagation();
            e.preventDefault();

            elements.dropZone.addClass("hover");
        }, false);

        elements.dropZone[0].addEventListener("dragleave", function (e) {
            e.stopPropagation();
            e.preventDefault();

            elements.dropZone.removeClass("hover");
        }, false);

        elements.dropZone[0].addEventListener("dragover", function (e) {
            e.preventDefault();
        }, false);

        elements.dropZone[0].addEventListener("drop", function (e) {
            e.stopPropagation();
            e.preventDefault();

            var reader = new FileReader();
            reader.onload = function (loaded) {
                elements.inputs.json.text(loaded.target.result);
            };

            reader.readAsText(e.dataTransfer.files[0]);
        }, false);

        elements.eventForm.submit(function (event) {
            event.preventDefault();

            var eventKey = elements.inputs.key.val();
            var eventType = elements.inputs.type.val();
            var json = elements.inputs.json.val();

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
                try {
                    json = JSON.parse(json);

                    bodata.bakula.sendEvent(eventType, eventKey, json, function (err, result) {
                        if (err != null) {
                            return alert("Event sending failed");
                        }

                        resetForm();
                        return alert("Event sent!");
                    });
                } catch (ex) {
                    alert("Failed parsing the provided JSON; unable to send to server.");
                }
            }
        });
    });
}());
