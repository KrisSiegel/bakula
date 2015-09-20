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
from bakula.security import iam, tokenutils
from bakula.services import user
from webtest import TestApp

test_app = TestApp(user.app)

class UserTest(unittest.TestCase):
    test_token = None

    @classmethod
    def setUpClass(self):
        UserTest.test_token = tokenutils.generate_auth_token('password', 'admin', 60)
        models.initialize_models({'database.name': ':memory:', 'database.type': 'sqlite'})

    def setUp(self):
        models.User.delete().execute()
        iam.create('admin', 'test_password')

    def test_create_user(self):
        response = test_app.post_json('/user', {
            'id': 'test_user',
            'password': 'some_password'
        }, headers={'Authorization': UserTest.test_token})

        self.assertEquals(response.status_int, 200)
        self.assertEquals(response.json['id'], 'test_user')
        user = models.User.get(models.User.id == 'test_user')
        self.assertIsNotNone(user)
        self.assertEquals(user.id, 'test_user')

    def test_create_user_already_exists(self):
        response = test_app.post_json('/user', {
            'id': 'admin',
            'password': 'some_password'
        }, expect_errors=True, headers={'Authorization': UserTest.test_token})

        self.assertEquals(response.status_int, 400)

    def test_create_user_non_admin(self):
        user_token = tokenutils.generate_auth_token('password', 'something_else', 60)
        response = test_app.post_json('/user', {
            'id': 'admin',
            'password': 'some_password'
        }, expect_errors=True, headers={'Authorization': user_token})
        self.assertEquals(response.status_int, 403)

    def test_login(self):
        response = test_app.post_json('/login', {
            'id': 'admin',
            'password': 'test_password'
        })
        self.assertEquals(response.status_int, 200)
        self.assertIsNotNone(response.json['token'])

    def test_login_bad_credentials(self):
        response = test_app.post_json('/login', {
            'id': 'admin',
            'password': 'wrong_password'
        }, expect_errors=True)
        self.assertEquals(response.status_int, 401)
        self.assertFalse('token' in response.json)

if __name__ == '__main__':
    unittest.main()