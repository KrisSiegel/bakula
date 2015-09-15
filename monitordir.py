#!/usr/bin/python

import os
import sys
import json
import time
import eventhandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

event_handler = eventhandler.EventHandler()

class MyWatcher(FileSystemEventHandler):
    def process(self, event):
        fakeJson = { }
        fakeJson["event_type"] = "filesystem"
        fakeJson["event_key"] = os.path.basename(os.path.dirname(os.path.realpath(event.src_path)))
        fakeJson["name"] = os.path.splitext(os.path.basename(event.src_path))[0]

        print "Sending event of type {0}, key {1} and {2}".format(fakeJson["event_type"], fakeJson["event_key"], fakeJson["name"])

        event_handler.send_event(fakeJson)

    def on_created(self, event):
        self.process(event)

if __name__ == "__main__":
    argument_count = len(sys.argv)

    if argument_count != 2:
        print "Only one specified directory allowed"
        sys.exit()

    directory = sys.argv[1]

    if not os.path.exists(directory):
        print "Specified directory does not exist"
        sys.exit()

    observer = Observer()
    observer.schedule(MyWatcher(), path = directory, recursive = False)
    observer.start()

    print "Monitoring {0} directory for files...".format(sys.argv[1])

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
            observer.stop()

    observer.join()
