# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing,
#   software distributed under the License is distributed on an
#   "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#   KIND, either express or implied.  See the License for the
#   specific language governing permissions and limitations
#   under the License.

import os
from atomiclong import AtomicLong

# class Inboxer provides basic capabilities to put a file in the master inbox,
# create a hardlink to that file in the correct container inboxes path and then
# delete the original file in the master inbox.
class Inboxer(object):
    # Initialize class with default paths to the master inbox and container
    # inboxes
    def __init__(self,
                 master_inbox_path="master_inbox",
                 container_inboxes_path="container_inboxes",
                 atomic_counter=AtomicLong(0)):
        self.master_inbox_path = master_inbox_path
        self.container_inboxes_path = container_inboxes_path
        self.atomic_counter = atomic_counter
        self.event_subscriptions = {} # Keep callbacks for events subscribed to
        self.count_cache = {} # Keep a cache of file counts; faster than recounting

        if not os.path.exists(self.master_inbox_path):
            os.makedirs(self.master_inbox_path)

        if not os.path.exists(self.container_inboxes_path):
            os.makedirs(self.container_inboxes_path)

    # This method is called to trigger an event
    def __trigger_event_subscription(self, event, data=None):
        if (event in self.event_subscriptions and
                self.event_subscriptions[event] is not None):
            self.event_subscriptions[event](data)

    def __get_file_count(self, topic):
        master_topic_path = os.path.join(self.master_inbox_path, topic)
        count = 0
        if os.path.exists(master_topic_path):
            for dirname, subdirs, files in os.walk(master_topic_path):
                for fname in files:
                    count = count + 1

        return count

    # Get a count from the cache count
    def __get_count_cache(self, topic):
        if topic not in self.count_cache:
            self.count_cache[topic] = __get_file_count(topic)
        return self.count_cache[topic]

    # Update the count cache
    def __update_count_cache(self, topic, count=None):
        if count is None:
            self.count_cache[topic] = self.__get_file_count(topic)
        else:
            self.count_cache[topic] = count

    # Registers a callback for a specific event
    # Don't care to support multiple registrations per event. Right now at
    # least.
    def on(self, event, callback):
        self.event_subscriptions[event] = callback

    # Takes a topic and a path to a file on the file system and moved it into
    # the master inbox removing it from its original location
    def add_file_by_path(self, topic, file_path):
        master_topic_path = os.path.join(self.master_inbox_path, topic)
        if not os.path.exists(master_topic_path):
            os.makedirs(master_topic_path)
        self.atomic_counter += 1
        counter = self.atomic_counter.value

        # Move into the master inbox under the correct topic with an updated
        # count
        destination = os.path.join(master_topic_path, str(counter))
        if os.path.exists(file_path):
            try:
                os.rename(file_path, destination)
            except Exception as ex:
                print "Writing to master inbox failed due to %s" % ex
                return None

        self.__update_count_cache(topic)
        self.__trigger_event_subscription("received", {"topic": topic})
        return counter

    # Takes a topic and data and writes it to the master inbox
    def add_file_by_bytes(self, topic, data):
        master_topic_path = os.path.join(self.master_inbox_path, topic)
        if not os.path.exists(master_topic_path):
            os.makedirs(master_topic_path)
        self.atomic_counter += 1
        counter = self.atomic_counter.value

        # Move into the master inbox under the correct topic with an updated
        # count
        destination = os.path.join(master_topic_path, str(counter))
        if not os.path.exists(destination):
            try:
                with open(destination, "w") as fout:
                    fout.write(data)
            except Exception as ex:
                print "Writing to master inbox failed due to %s" % ex
                return None

        self.__update_count_cache(topic)
        self.__trigger_event_subscription("received", {"topic": topic})
        return counter

    # Gets a listing of files currently in the master queue for the specified
    # topic
    def get_inbox_list(self, topic):
        master_topic_path = os.path.join(self.master_inbox_path, topic)
        result = []
        if os.path.exists(master_topic_path):
            for dirname, subdirs, files in os.walk(master_topic_path):
                for fname in files:
                    result.append(fname)

        return result

    # Get a count of files in the master inbox for a specific topic
    def get_inbox_count(self, topic):
        return self.__get_count_cache(topic)

    # Promotes a file from the master inbox into a container inbox delineated
    # by container id
    def promote_to_container_inbox(self, topic, containerids):
        promotees = self.get_inbox_list(topic)
        container_inboxes = []
        if len(promotees) > 0:

            # Since we allow a single, string or an array of strings for the
            # containerids parameter, let's make a variable that's always an
            # array for our loop
            isArray = not isinstance(containerids, basestring)
            containerids = containerids if isArray else [containerids]

            for containerid in containerids:
                container_inbox_path = os.path.join(
                    self.container_inboxes_path, containerid)
                if not os.path.exists(container_inbox_path):
                    os.makedirs(container_inbox_path)

                for fname in promotees:
                    try:
                        fullpath = os.path.join(self.master_inbox_path,
                                                topic,
                                                fname)
                        destination = os.path.join(container_inbox_path, fname)
                        os.link(fullpath, destination)
                        container_inboxes.append(destination)
                    except Exception as ex:
                        print "Generating hard links failed due to %s" % ex
                        return None

            for fname in promotees:
                fullpath = os.path.join(self.master_inbox_path, topic, fname)
                if os.stat(fullpath).st_nlink > 0:
                    # Hard link created successfully; delete the original
                    try:
                        os.remove(fullpath)
                    except Exception as ex:
                        print ("Deleting master inbox files after promotion"
                               "failed due to %s") % ex
                        return None
                else:
                    print "Failure creating hard link on %s" % fullpath

            self.__update_count_cache(topic)
            return container_inboxes
