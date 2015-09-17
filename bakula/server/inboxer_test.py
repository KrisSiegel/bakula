import unittest
import os
import uuid
import shutil
from inboxer import Inboxer

class InboxerTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        shutil.rmtree(".tmp", ignore_errors=True)

    def test_currentUpperBound(self):
        path = os.path.join(".tmp", uuid.uuid1().hex)
        os.makedirs(path)
        testPath0 = os.path.join(path, "0")
        testPath1 = os.path.join(path, "1")
        testPath2 = os.path.join(path, "2")
        with open(testPath0, "a"):
            os.utime(testPath0, None)
        with open(testPath1, "a"):
            os.utime(testPath0, None)
        with open(testPath2, "a"):
            os.utime(testPath0, None)

        self.assertEqual(2, Inboxer.currentUpperBound(path))

    def test_addFileByPath(self):
        masterInboxPath = os.path.join(".tmp", "master_inbox")
        containerInboxesPath = os.path.join(".tmp", "container_inboxes")
        testFile = os.path.join(".tmp", "testFile.json")

        # Initialize inboxer using a tmp directory for unit testing
        inboxer = Inboxer(masterInboxPath, containerInboxesPath)

        # Create our test file
        with open(testFile, "a"):
            os.utime(testFile, None)

        masterInboxDestination = os.path.join(masterInboxPath, "MyTopic", "0")

        self.assertEqual(os.path.exists(masterInboxDestination), False)
        inboxer.addFileByPath("MyTopic", testFile)
        self.assertEqual(os.path.exists(testFile), False)
        self.assertEqual(os.path.exists(masterInboxDestination), True)

    def test_getInboxList(self):
        masterInboxPath = os.path.join(".tmp", "master_inbox")
        containerInboxesPath = os.path.join(".tmp", "container_inboxes")
        testFile1 = os.path.join(".tmp", "testFile1.json")
        testFile2 = os.path.join(".tmp", "testFile2.json")
        testFile3 = os.path.join(".tmp", "testFile3.json")

        # Initialize inboxer using a tmp directory for unit testing
        inboxer = Inboxer(masterInboxPath, containerInboxesPath)

        # Create our test files
        with open(testFile1, "a"):
            os.utime(testFile1, None)

        with open(testFile2, "a"):
            os.utime(testFile2, None)

        with open(testFile3, "a"):
            os.utime(testFile3, None)

        inboxer.addFileByPath("MyTopic", testFile1)
        inboxer.addFileByPath("MyTopic", testFile2)
        inboxer.addFileByPath("MyTopic", testFile3)

        self.assertEqual(len(inboxer.getInboxList("MyTopic")), 3)

    def test_promoteToContainerInbox(self):
        masterInboxPath = os.path.join(".tmp", "master_inbox")
        containerInboxesPath = os.path.join(".tmp", "container_inboxes")
        testFile1 = os.path.join(".tmp", "testFile1.json")
        testFile2 = os.path.join(".tmp", "testFile2.json")
        testFile3 = os.path.join(".tmp", "testFile3.json")

        # Initialize inboxer using a tmp directory for unit testing
        inboxer = Inboxer(masterInboxPath, containerInboxesPath)

        # Create our test files
        with open(testFile1, "a"):
            os.utime(testFile1, None)

        with open(testFile2, "a"):
            os.utime(testFile2, None)

        with open(testFile3, "a"):
            os.utime(testFile3, None)

        inboxer.addFileByPath("MyTopic", testFile1)
        inboxer.addFileByPath("MyTopic", testFile2)
        inboxer.addFileByPath("MyTopic", testFile3)

        self.assertEqual(len(inboxer.getInboxList("MyTopic")), 3)

        inboxer.promoteToContainerInbox("MyTopic", "RandomContainerIDHere")

        self.assertEqual(len(inboxer.getInboxList("MyTopic")), 0)

if __name__ == '__main__':
    unittest.main()
