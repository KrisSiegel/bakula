import unittest
import os
import shutil
from inboxer import Inboxer

class InboxerTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        shutil.rmtree(".tmp", ignore_errors=True)

    def test_add_file_by_path(self):
        master_inbox_path = os.path.join(".tmp", "master_inbox")
        container_inboxes_path = os.path.join(".tmp", "container_inboxes")
        testfile = os.path.join(".tmp", "testFile.json")

        # Initialize inboxer using a tmp directory for unit testing
        inboxer = Inboxer(master_inbox_path, container_inboxes_path)

        # Create our test file
        with open(testfile, "a"):
            os.utime(testfile, None)

        counter = inboxer.add_file_by_path("MyTopic", testfile)
        master_inbox_destination = os.path.join(master_inbox_path, "MyTopic", str(counter))
        self.assertEqual(os.path.exists(testfile), False)
        self.assertEqual(os.path.exists(master_inbox_destination), True)

    def test_get_inbox_list(self):
        master_inbox_path = os.path.join(".tmp", "master_inbox")
        container_inboxes_path = os.path.join(".tmp", "container_inboxes")
        testfile1 = os.path.join(".tmp", "testFile1.json")
        testfile2 = os.path.join(".tmp", "testFile2.json")
        testfile3 = os.path.join(".tmp", "testFile3.json")

        # Initialize inboxer using a tmp directory for unit testing
        inboxer = Inboxer(master_inbox_path, container_inboxes_path)

        # Create our test files
        with open(testfile1, "a"):
            os.utime(testfile1, None)

        with open(testfile2, "a"):
            os.utime(testfile2, None)

        with open(testfile3, "a"):
            os.utime(testfile3, None)

        inboxer.add_file_by_path("MyTopic", testfile1)
        inboxer.add_file_by_path("MyTopic", testfile2)
        inboxer.add_file_by_path("MyTopic", testfile3)
        
        self.assertEqual(len(inboxer.get_inbox_list("MyTopic")), 3)

    def test_promote_to_container_inbox(self):
        master_inbox_path = os.path.join(".tmp", "master_inbox")
        container_inboxes_path = os.path.join(".tmp", "container_inboxes")
        testfile1 = os.path.join(".tmp", "testFile1.json")
        testfile2 = os.path.join(".tmp", "testFile2.json")
        testfile3 = os.path.join(".tmp", "testFile3.json")

        # Initialize inboxer using a tmp directory for unit testing
        inboxer = Inboxer(master_inbox_path, container_inboxes_path)

        # Create our test files
        with open(testfile1, "a"):
            os.utime(testfile1, None)

        with open(testfile2, "a"):
            os.utime(testfile2, None)

        with open(testfile3, "a"):
            os.utime(testfile3, None)

        inboxer.add_file_by_path("MyTopic", testfile1)
        inboxer.add_file_by_path("MyTopic", testfile2)
        inboxer.add_file_by_path("MyTopic", testfile3)

        self.assertEqual(len(inboxer.get_inbox_list("MyTopic")), 3)

        inboxer.promote_to_container_inbox("MyTopic", "RandomContainerIDHere")

        self.assertEqual(len(inboxer.get_inbox_list("MyTopic")), 0)

if __name__ == '__main__':
    unittest.main()
