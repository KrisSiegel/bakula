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

import unittest
import os
import shutil
import tempfile
from inboxer import Inboxer

class InboxerTest(unittest.TestCase):

    TEST_DIR = os.path.join(tempfile.gettempdir(), 'inboxer_test')

    def setUp(self):
        pass

    def tearDown(self):
        shutil.rmtree(self.TEST_DIR, ignore_errors=True)

    def test_on(self):
        def callback(data):
            self.assertEqual(data["topic"], "MyTopicEvent")

        master_inbox_path = os.path.join(self.TEST_DIR, "master_inbox")
        container_inboxes_path = os.path.join(self.TEST_DIR, "container_inboxes")
        testfile = os.path.join(self.TEST_DIR, "testFile.json")

        # Initialize inboxer using a tmp directory for unit testing
        inboxer = Inboxer(master_inbox_path, container_inboxes_path)

        inboxer.on("received", callback)
        # Create our test file
        with open(testfile, "a"):
            os.utime(testfile, None)

        counter = inboxer.add_file_by_path("MyTopicEvent", testfile)

    def test_add_file_by_path(self):
        master_inbox_path = os.path.join(self.TEST_DIR, "master_inbox")
        container_inboxes_path = os.path.join(self.TEST_DIR, "container_inboxes")
        testfile = os.path.join(self.TEST_DIR, "testFile.json")

        # Initialize inboxer using a tmp directory for unit testing
        inboxer = Inboxer(master_inbox_path, container_inboxes_path)

        # Create our test file
        with open(testfile, "a"):
            os.utime(testfile, None)

        counter = inboxer.add_file_by_path("MyTopic", testfile)
        master_inbox_destination = os.path.join(master_inbox_path,
                                                "MyTopic",
                                                str(counter))
        self.assertEqual(os.path.exists(testfile), False)
        self.assertEqual(os.path.exists(master_inbox_destination), True)

    def test_add_file_by_bytes(self):
        master_inbox_path = os.path.join(self.TEST_DIR, "master_inbox")
        container_inboxes_path = os.path.join(self.TEST_DIR, "container_inboxes")

        # Initialize inboxer using a tmp directory for unit testing
        inboxer = Inboxer(master_inbox_path, container_inboxes_path)

        counter = inboxer.add_file_by_bytes("MyTopic",
                                            "This is a test file weeee")
        master_inbox_destination = os.path.join(master_inbox_path,
                                                "MyTopic",
                                                str(counter))
        self.assertEqual(os.path.exists(master_inbox_destination), True)

    def test_get_inbox_list(self):
        master_inbox_path = os.path.join(self.TEST_DIR, "master_inbox")
        container_inboxes_path = os.path.join(self.TEST_DIR, "container_inboxes")
        testfile1 = os.path.join(self.TEST_DIR, "testFile1.json")
        testfile2 = os.path.join(self.TEST_DIR, "testFile2.json")
        testfile3 = os.path.join(self.TEST_DIR, "testFile3.json")

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

    def test_get_inbox_count(self):
        master_inbox_path = os.path.join(self.TEST_DIR, "master_inbox")
        container_inboxes_path = os.path.join(self.TEST_DIR, "container_inboxes")
        testfile1 = os.path.join(self.TEST_DIR, "testFile1.json")
        testfile2 = os.path.join(self.TEST_DIR, "testFile2.json")
        testfile3 = os.path.join(self.TEST_DIR, "testFile3.json")

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

        self.assertEqual(inboxer.get_inbox_count("MyTopic"), 3)

    def test_promote_to_container_inbox(self):
        master_inbox_path = os.path.join(self.TEST_DIR, "master_inbox")
        container_inboxes_path = os.path.join(self.TEST_DIR, "container_inboxes")
        testfile1 = os.path.join(self.TEST_DIR, "testFile1.json")
        testfile2 = os.path.join(self.TEST_DIR, "testFile2.json")
        testfile3 = os.path.join(self.TEST_DIR, "testFile3.json")

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
        inboxer.add_file_by_path("MyTopic3", testfile3)

        self.assertEqual(len(inboxer.get_inbox_list("MyTopic")), 2)

        inboxer.promote_to_container_inbox("MyTopic", "RandomContainerIDHere")

        self.assertEqual(len(inboxer.get_inbox_list("MyTopic")), 0)

        self.assertEqual(len(inboxer.get_inbox_list("MyTopic3")), 1)

        inboxer.promote_to_container_inbox("MyTopic3",
                                           ["Container1",
                                            "Container2",
                                            "Container3"])

        self.assertEqual(len(inboxer.get_inbox_list("MyTopic3")), 0)

if __name__ == '__main__':
    unittest.main()
