/*
    ./lib/bakula-api.js

    The API used to communicate with the bakula endpoints.
*/
var bodata = bodata || { };
bodata.bakula = (function () {
    "using strict";

    return {
        register: function (name, eventType, eventKey, files, callback) {
            var data = new FormData();
            data.append("image_name", name);
            data.append("event_key", eventKey);
            data.append("event_type", eventType);
            data.append("file", files[0]);

            jQuery.ajax({
                url: config.server + "register",
                method: "POST",
                data: data,
                contentType: false,
                processData: false,
                xhrFields: {
                    withCredentials: true
                },
                success: function (data, status, xhr) {
                    if (callback !== undefined) {
                        callback.apply(this, [null, data]);
                    }
                },
                error: function (xhr, status, error) {
                    if (callback !== undefined) {
                        callback.apply(this, [error || status, null]);
                    }
                }
            });
        },
        sendEvent: function (type, key, json, callback) {
            json.event_type = type;
            json.event_key = key;

            jQuery.ajax({
                url: config.server + "events",
                method: "POST",
                data: JSON.stringify(json),
                contentType: "application/json",
                xhrFields: {
                    withCredentials: true
                },
                success: function (data, status, xhr) {
                    if (callback !== undefined) {
                        callback.apply(this, [null, data]);
                    }
                },
                error: function (xhr, status, error) {
                    if (callback !== undefined) {
                        callback.apply(this, [error || status, null]);
                    }
                }
            });
        },
        login: function (username, password, callback) {
            jQuery.ajax({
                url: config.server + "users/login",
                method: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    username: username,
                    password: password
                }),
                xhrFields: {
                    withCredentials: true
                },
                success: function (data, status, xhr) {
                    if (callback !== undefined) {
                        callback.apply(this, [null, data]);
                    }
                },
                error: function (xhr, status, error) {
                    if (callback !== undefined) {
                        callback.apply(this, [error || status, null]);
                    }
                }
            });
        }
    };
}());
