#!/usr/bin/python

import os

# class Inboxer provides basic capabilities to put a file in the master inbox,
# create a hardlink to that file in the correct container inboxes path and then
# delete the original file in the master inbox.
class Inboxer:
    # Initialize class with default paths to the master inbox and container inboxes
    def __init__(self, master_inbox_path="master_inbox", container_inboxes_path="container_inboxes"):
        self.master_inbox_path = master_inbox_path
        self.container_inboxes_path = container_inboxes_path

        if not os.path.exists(self.master_inbox_path):
            os.makedirs(self.master_inbox_path)

        if not os.path.exists(self.container_inboxes_path):
            os.makedirs(self.container_inboxes_path)

    # Private, static method to check if a string contains just a number or not
    @staticmethod
    def __is_number(str):
        try:
            int(str)
            return True
        except ValueError:
            return False

    # Static method that uses filenames to find the next number regardless
    # of modified or created times
    @staticmethod
    def current_upper_bound(dir):
        file_name_number = -1
        for dirname, subdirs, files in os.walk(dir):
            for fname in files:
                if Inboxer.__is_number(fname):
                    number = int(fname)
                    if number > file_name_number:
                        file_name_number = number

        return file_name_number

    # Takes a topic and a path to a file on the file system and moved it into
    # the master inbox removing it from its original location
    def add_file_by_path(self, topic, file_path):
        master_topic_path = os.path.join(self.master_inbox_path, topic)
        if not os.path.exists(master_topic_path):
            os.makedirs(master_topic_path)
        next_count = Inboxer.current_upper_bound(master_topic_path) + 1

        # Move into the master inbox under the correct topic with an updated count
        destination = os.path.join(master_topic_path, str(next_count))
        if os.path.exists(file_path):
            os.rename(file_path, destination)

    # Gets a listing of files currently in the master queue for the specified topic
    def get_inbox_list(self, topic):
        master_topic_path = os.path.join(self.master_inbox_path, topic)
        result = []
        if os.path.exists(master_topic_path):
            for dirname, subdirs, files in os.walk(master_topic_path):
                for fname in files:
                    result.extend(fname)

        return result

    # Promotes a file from the master inbox into a container inbox delineated by container id
    def promote_to_container_inbox(self, topic, containerid):
        promotees = self.get_inbox_list(topic)
        if len(promotees) > 0:
            container_inboxes_path = os.path.join(self.container_inboxes_path, containerid)
            if not os.path.exists(container_inboxes_path):
                os.makedirs(container_inboxes_path)

            for fname in promotees:
                fullpath = os.path.join(self.master_inbox_path, topic, fname)
                destination = os.path.join(container_inboxes_path, fname)
                os.link(fullpath, destination)

                if os.stat(fullpath).st_nlink > 0:
                    # Hard link created successfully; delete the original
                    os.remove(fullpath);
                else:
                    print "Failure creating hard link on " + fullpath
