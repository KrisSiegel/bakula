#!/usr/bin/python

from flask import Flask
from flask import request
from flask import json

import eventhandler

app = Flask(__name__)

event_handler = eventhandler.EventHandler()

@app.route('/register', methods = ['POST'])
def register():
    if request.headers['Content-Type'] == 'application/json':
       event_handler.register_image(request.json)
    return "Registered"


@app.route('/events', methods = ['POST'])
def handle():
    if request.headers['Content-Type'] == 'application/json':
       event_handler.send_event(request.json)
    return "It worked :)"
    
if __name__ == '__main__':
    app.run(debug=True)
