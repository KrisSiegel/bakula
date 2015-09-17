import unittest
import os
from peewee import SqliteDatabase, Model, CharField
from bakula import models

TEST_DB_FILE = 'test.db'

if os.path.exists(TEST_DB_FILE):
    os.remove(TEST_DB_FILE)
test_db = SqliteDatabase(TEST_DB_FILE)

class TestModel(Model):
    name = CharField()
    message = CharField()

    class Meta:
        database = test_db

class ModelsTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        test_db.connect()
        TestModel.create_table()
        obj = TestModel(name='test', message='this is a test model')
        obj.save()

    @classmethod
    def tearDownClass(self):
        test_db.close()
        os.remove(TEST_DB_FILE)

    def test_resolve_query(self):
        results = models.resolve_query(TestModel.select().where(TestModel.name == 'test'))
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], dict) # Make sure this is a dict and not a TestModel
        self.assertEqual(results[0]['name'], 'test')

if __name__ == '__main__':
    unittest.main()