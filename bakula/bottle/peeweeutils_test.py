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
import peeweeutils
import bottle
from peewee import *

class PeeweeutilsTest(unittest.TestCase):

    def test_no_config(self):
        with self.assertRaises(RuntimeError):
            peeweeutils.get_db_from_config(None)

    def test_no_database_type(self):
        config = {'database': {'user': 'john', 'name': ':memory:'}}
        app = bottle.Bottle()
        app.config.load_dict(config)
        with self.assertRaises(RuntimeError):
            peeweeutils.get_db_from_config(app.config)

    def test_invalid_database_type(self):
        config = {'database': {'type': 'barrydb', 'user': 'john',
                               'name': ':memory:'}}
        app = bottle.Bottle()
        app.config.load_dict(config)
        with self.assertRaises(RuntimeError):
            peeweeutils.get_db_from_config(config)

    def test_no_database_name(self):
        config = {'database': {'type': 'barrydb', 'user': 'john'}}
        app = bottle.Bottle()
        app.config.load_dict(config)
        with self.assertRaises(RuntimeError):
            peeweeutils.get_db_from_config(config)

    def test_valid(self):
        config = {'database': {'type': 'sqlite', 'user': 'john',
                               'name': ':memory:'}}
        app = bottle.Bottle()
        app.config.load_dict(config)
        db = peeweeutils.get_db_from_config(config)
        self.assertEquals(type(db), SqliteDatabase)

if __name__ == '__main__':
    unittest.main()
