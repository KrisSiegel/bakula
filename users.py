#!/usr/bin/python

import os
import json

class Bucket:
    pass

class Users:
    def __init__(self):
        self.filepath = "users.json"

    def getAll(self):
        with open(self.filepath, "r") as data:
            contents = json.load(data)
            return contents

    def login(self, obj):
        with open(self.filepath, "r") as data:
            contents = json.load(data)
            result = Bucket()
            result.message = "Login successful"
            result.status_code = 200
            return result
