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
import shutil
import os
from bakula.services import event
from webtest import TestApp
from bakula import models
from bakula.security import tokenutils, iam

test_app = TestApp(event.app)

class EventTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        models.initialize_models({'database.name': ':memory:',
                                  'database.type': 'sqlite'})
        iam.create('user', 'some_password')
        EventTest.auth_header = {
            'Authorization': tokenutils.generate_auth_token(
                'password',
                'user',
                120)
        }

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
        }, upload_files=[("data[]", testfile)], expect_errors=False, headers=EventTest.auth_header)

        self.assertEqual(response.status_int, 201)

if __name__ == '__main__':
    unittest.main()
