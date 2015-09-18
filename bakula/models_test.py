import unittest
import os
from peewee import Model, CharField, Proxy
from bakula import models
from bakula.bottle import peeweeutils

test_db = Proxy()
class TestModel(Model):
    name = CharField()
    message = CharField()

    class Meta:
        database = test_db

class ModelsTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        peeweeutils.get_db_from_config({'sqlite_database': ':memory:', 'databaseType': 'sqlite'}, test_db)
        TestModel.create_table()
        obj = TestModel(name='test', message='this is a test model')
        obj.save()

    @classmethod
    def tearDownClass(self):
        test_db.close()

    def test_resolve_query(self):
        results = models.resolve_query(TestModel.select().where(TestModel.name == 'test'))
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], dict) # Make sure this is a dict and not a TestModel
        self.assertEqual(results[0]['name'], 'test')

    def test_initialize_models(self):
        models.initialize_models({'sqlite_database': ':memory:', 'databaseType': 'sqlite'})
        self.assertTrue(models.Registration.table_exists())
        self.assertTrue(models.User.table_exists())

if __name__ == '__main__':
    unittest.main()