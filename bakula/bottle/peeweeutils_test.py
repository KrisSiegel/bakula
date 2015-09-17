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
import peeweeutils
from peewee import *

class PeeweeutilsTest(unittest.TestCase):

    def test_no_config(self):
        with self.assertRaises(RuntimeError):
            peeweeutils.get_db_from_config(None)

    def test_no_database_type(self):
        config = {'postgres_database' : 'cookie', 'postgres_user' : 'john'}
        with self.assertRaises(RuntimeError):
            peeweeutils.get_db_from_config(config)

    def test_invalid_database_type(self):
        config = {'databaseType' : 'mysql'}
        with self.assertRaises(RuntimeError):
            peeweeutils.get_db_from_config(config)

    def test_no_database_specified(self):
        config = {'databaseType' : 'postgres', 'postgres_user' : 'john'}
        with self.assertRaises(RuntimeError):
            peeweeutils.get_db_from_config(config)

    def test_valid(self):
        config = {'databaseType' : 'sqlite', 'sqlite_user' : 'john',
                'sqlite_database' : ':memory:'}
        db = peeweeutils.get_db_from_config(config)
        self.assertEquals(type(db), SqliteDatabase)


if __name__ == '__main__':
    unittest.main()
