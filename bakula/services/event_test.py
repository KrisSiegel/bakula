# Copyright 2015 Immuta, Inc. Licensed under the Immuta Software License
# Version 0.1 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#
#    http://www.immuta.com/licenses/Immuta_Software_License_0.1.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import unittest
import shutil
import os
from bakula.services import event
from webtest import TestApp

test_app = TestApp(event.app)

class EventTest(unittest.TestCase):

    def tearDown(self):
        shutil.rmtree(".tmp", ignore_errors=True)

    def test_post_event(self):
        os.makedirs(".tmp")
        testfile = os.path.join(".tmp", "testFile.json")
        # Create our test file
        with open(testfile, "w+") as fout:
            fout.write("stuff")

        response = test_app.post("/event", {
            "topic": "MyTopic"
        }, upload_files=[("data[]", testfile)], expect_errors=False)

        self.assertEqual(response.status_int, 201)

if __name__ == '__main__':
    unittest.main()
