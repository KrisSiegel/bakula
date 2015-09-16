#!/usr/bin/python

import eventhandler
import users
import os

from flask import Flask, request, json, jsonify, send_from_directory
from werkzeug import secure_filename

app = Flask(__name__, static_folder="ui")

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['tar', 'tar.gz', 'tar.bz', 'zip'])

event_handler = eventhandler.EventHandler()
users = users.Users()

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/register', methods = ['POST'])
def register():
    f = request.files['file']
    path = None
    if f and allowed_file(f.filename):
        filename = secure_filename(f.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(path):
            os.remove(path)
        f.save(path)
    image_name = request.form['image_name']
    event_type = request.form['event_type']
    event_key  = request.form['event_key']
    print event_type
    print event_key
    event_handler.register_image(event_type, event_key, image_name, path)
    return "Listening for events of type %s with key of %s" % (event_type, event_key), 200

@app.route("/")
def index():
    return app.send_static_file("index.html"), 200

@app.route("/<path:path>")
def root(path):
    return send_from_directory("ui", path), 200

@app.route('/events', methods = ['POST'])
def handle():
    event_handler.send_event(request.json)
    return "Successful", 200

@app.route("/users", methods = ["GET"])
def userList():
    return jsonify(users.getAll()), 200

@app.route("/users/login", methods = ["POST"])
def login():
    result = users.login(request.json)
    return result.message, result.status_code

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4242)
