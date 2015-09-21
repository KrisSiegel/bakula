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
from bakula import models
from bakula.security import iam

class ModelsTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        models.initialize_models({'database.name': ':memory:',
                                  'database.type': 'sqlite'})

    def test_authenticate(self):
        authenticated = iam.authenticate('admin', 'secret')
        self.assertTrue(authenticated)

    def test_authenticate_bad_creds(self):
        authenticated = iam.authenticate('admin', 'wrong_pw')
        self.assertFalse(authenticated)

    def test_create_user(self):
        created = iam.create('user', 'password')
        self.assertTrue(created)
        authenticated = iam.authenticate('user', 'password')
        self.assertTrue(authenticated)

    def test_create_duplicate_user(self):
        created = iam.create('admin', 'some_password')
        self.assertFalse(created)

if __name__ == '__main__':
    unittest.main()
