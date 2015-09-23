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
from time import sleep

from inboxer import Inboxer
from bakula import models
from bakula.models import Registration
from bakula.docker import dockeragent
from orchestrator import Orchestrator
import time

DOCKER_TIMEOUT = 10
class OrchestratorTest(unittest.TestCase):
    TEST_DIR = os.path.join(tempfile.gettempdir(), 'orchestrator_test')

    @classmethod
    def setUpClass(self):
        models.initialize_models({'database.name': ':memory:',
                                  'database.type': 'sqlite'})

    def setUp(self):
        Registration.delete().execute()

    def tearDown(self):
        shutil.rmtree(self.TEST_DIR, ignore_errors=True)
        models.Registration.delete().execute()
        # allow the cleanup thread to remove old containers
        time.sleep(10)

    def test_Orchestrator_with_threshold(self):
        Registration.create(
            topic="MyTopic1",
            container="busybox",
            creator="me",
            threshold=1,
            timeout=15
        )

        inboxer = Inboxer(os.path.join(self.TEST_DIR, "master_inbox"),
                          os.path.join(self.TEST_DIR, "container_inboxes"))
        orchestrator = Orchestrator(inboxer)
        inboxer.add_file_by_bytes("MyTopic1", "This is some data")
        self.assertEqual(len(inboxer.get_inbox_list("MyTopic1")), 0)

    def test_Orchestrator_with_timeout(self):
        Registration.create(
            topic="MyTopic2",
            container="busybox",
            creator="me",
            threshold=100,
            timeout=5
        )

        inboxer = Inboxer(os.path.join(self.TEST_DIR, "master_inbox"),
                          os.path.join(self.TEST_DIR, "container_inboxes"))
        orchestrator = Orchestrator(inboxer)
        inboxer.add_file_by_bytes("MyTopic2", "This is some data")
        sleep(20)
        self.assertEqual(len(inboxer.get_inbox_list("MyTopic2")), 0)

if __name__ == '__main__':
    unittest.main()
