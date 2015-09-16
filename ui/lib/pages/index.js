/*
    ./lib/pages/index.js

    This is the controller for the index.html web page
*/
var pages = pages || { };
pages.index = (function () {
    "using strict";

    jQuery(document).ready(function () {

        var elements = {
            dropZone: jQuery("#dropZone"),
            dropZoneText: jQuery("#dropZone > p"),
            logoutBtn: jQuery("#logoutBtn"),
            registrationForm: jQuery("#registrationForm"),
            inputs: {
                name: jQuery("#containerName"),
                key: jQuery("#eventKey"),
                type: jQuery("#eventType"),
                file: jQuery("#containerFile")
            }
        };

        var currentFiles;

        var validInput = "abcdefghijklmnopqrstuvwxyz_.0123456789";
        var validFileExts = ['tar', 'tar.gz', 'tar.bz', 'zip'];

        var validateFileName = function (name) {
            var splits = name.split(".");
            var ext;
            if (splits.length === 3) {
                var pop1 = splits.pop();
                var pop2 = splits.pop();
                ext = pop2 + "." + pop1;
            } else if (splits.length > 0){
                ext = splits.pop();
            }

            if (validFileExts.indexOf(ext) === -1) {
                elements.inputs.file.parent().removeClass("has-success");
                elements.inputs.file.parent().addClass("has-error");
            } else {
                elements.inputs.file.parent().addClass("has-success");
                elements.inputs.file.parent().removeClass("has-error");
            }
        };

        var resetForm = function (e) {
            if (e === undefined) {
                // Manually called
                elements.registrationForm[0].reset();
            }
            elements.dropZoneText.text("To upload click here or drag and drop a container");
            for (var field in elements.inputs) {
                if (elements.inputs.hasOwnProperty(field)) {
                    elements.inputs[field].parent().removeClass("has-success");
                    elements.inputs[field].parent().removeClass("has-error");
                }
            }
        };

        elements.registrationForm.on("reset", resetForm);

        elements.inputs.name.on("change", function (e) {
            pages.common.validateText(elements.inputs.name, validInput);
        });

        elements.inputs.key.on("change", function (e) {
            pages.common.validateText(elements.inputs.key, validInput);
        });

        elements.inputs.type.on("change", function (e) {
            pages.common.validateText(elements.inputs.type, validInput);
        });

        elements.inputs.file.on("change", function () {
            currentFiles = this.files;
            elements.dropZoneText.text(currentFiles[0].name);
            validateFileName(currentFiles[0].name);
        });

        elements.logoutBtn.click(function (event) {
            alert("Users not yet implemented. This is a stub :)");
        });

        elements.dropZone.click(function (event) {
            elements.inputs.file.click();
        });

        elements.dropZone[0].addEventListener("dragenter", function (e) {
            e.stopPropagation();
            e.preventDefault();

            elements.dropZoneText.text("Drop it! Do it! Come on, you know you want to!");
            elements.dropZone.addClass("hover");
        }, false);

        elements.dropZone[0].addEventListener("dragleave", function (e) {
            e.stopPropagation();
            e.preventDefault();

            elements.dropZoneText.text("To upload click here or drag and drop a container");
            elements.dropZone.removeClass("hover");
        }, false);

        elements.dropZone[0].addEventListener("dragover", function (e) {
            e.preventDefault();
        }, false);

        elements.dropZone[0].addEventListener("drop", function (e) {
            e.stopPropagation();
            e.preventDefault();

            currentFiles = e.dataTransfer.files;
            elements.dropZoneText.text(currentFiles[0].name);

            validateFileName(currentFiles[0].name);
        }, false);

        elements.registrationForm.submit(function (event) {
            event.preventDefault();

            var name = elements.inputs.name.val();
            var eventKey = elements.inputs.key.val();
            var eventType = elements.inputs.type.val();

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
                bodata.bakula.register(name, eventType, eventKey, currentFiles, function (err, result) {
                    if (err != null) {
                        return alert("Registration failed");
                    }

                    resetForm();
                    return alert("Registration saved!");
                });
            }
        });
    });
}());
