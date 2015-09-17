#!/usr/bin/python

import os

# class Inboxer provides basic capabilities to put a file in the master inbox,
# create a hardlink to that file in the correct container inboxes path and then
# delete the original file in the master inbox.
class Inboxer:
    # Initialize class with default paths to the master inbox and container inboxes
    def __init__(self, masterInboxPath="master_inbox", containerInboxesPath="container_inboxes"):
        self.masterInboxPath = masterInboxPath
        self.containerInboxesPath = containerInboxesPath

        if not os.path.exists(self.masterInboxPath):
            os.makedirs(self.masterInboxPath)

        if not os.path.exists(self.containerInboxesPath):
            os.makedirs(self.containerInboxesPath)

    # Private, static method to check if a string contains just a number or not
    @staticmethod
    def __isNumber(str):
        try:
            int(str)
            return True
        except ValueError:
            return False

    # Static method that uses filenames to find the next number regardless
    # of modified or created times
    @staticmethod
    def currentUpperBound(dir):
        fileNameNumber = -1
        for dirname, subdirs, files in os.walk(dir):
            for fileName in files:
                if Inboxer.__isNumber(fileName):
                    number = int(fileName)
                    if number > fileNameNumber:
                        fileNameNumber = number

        return fileNameNumber

    # Takes a topic and a path to a file on the file system and moved it into
    # the master inbox removing it from its original location
    def addFileByPath(self, topic, filePath):
        masterTopicPath = os.path.join(self.masterInboxPath, topic)
        if not os.path.exists(masterTopicPath):
            os.makedirs(masterTopicPath)
        nextCount = Inboxer.currentUpperBound(masterTopicPath) + 1

        # Move into the master inbox under the correct topic with an updated count
        destination = os.path.join(masterTopicPath, str(nextCount))
        if os.path.exists(filePath):
            os.rename(filePath, destination)

    # Gets a listing of files currently in the master queue for the specified topic
    def getInboxList(self, topic):
        masterTopicPath = os.path.join(self.masterInboxPath, topic)
        result = []
        if os.path.exists(masterTopicPath):
            for dirname, subdirs, files in os.walk(masterTopicPath):
                for fileName in files:
                    result.extend(fileName)

        return result

    # Promotes a file from the master inbox into a container inbox delineated by container id
    def promoteToContainerInbox(self, topic, containerId):
        promotees = self.getInboxList(topic)
        if len(promotees) > 0:
            containerInboxPath = os.path.join(self.containerInboxesPath, containerId)
            if not os.path.exists(containerInboxPath):
                os.makedirs(containerInboxPath)

            for fileName in promotees:
                fullPath = os.path.join(self.masterInboxPath, topic, fileName)
                destination = os.path.join(containerInboxPath, fileName)
                os.link(fullPath, destination)

                if os.stat(fullPath).st_nlink > 0:
                    # Hard link created successfully; delete the original
                    os.remove(fullPath);
                else:
                    print "Failure creating hard link on " + fullPath
