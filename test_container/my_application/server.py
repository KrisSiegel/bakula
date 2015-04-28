#!/usr/bin/python

from flask import Flask,request,json

FILE_NAME = 'bar.txt'

app = Flask(__name__)

@app.route('/')
def root():
    return "Hello, From The Container!"

@app.route("/events", methods=['POST'])
def events():
     if request.headers['Content-Type'] == 'application/json':
        with open(FILE_NAME, "a") as my_file:
            my_file.write(json.dumps(request.json))
            my_file.write("\n")
     return "All Good"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
