import unittest
from bakula import models
from bakula.services import registration
from bakula.security import tokenutils, iam
from webtest import TestApp

test_app = TestApp(registration.app)

class RegistrationTest(unittest.TestCase):
    auth_header = None
    test_user = None

    @classmethod
    def setUpClass(self):
        models.initialize_models({'sqlite_database': ':memory:', 'databaseType': 'sqlite'})
        iam.create('user', 'some_password')
        RegistrationTest.test_user = models.User.get(models.User.id == 'user')
        RegistrationTest.auth_header = {'Authorization': tokenutils.generate_auth_token('password', RegistrationTest.test_user.id, 120)}

    def setUp(self):
        models.Registration.delete().execute()

    def test_create_registration(self):
        topic = 'some_topic'
        response = test_app.post_json('/registration', {
            'topic': topic,
            'container': 'not_a_real_container'
        }, headers=RegistrationTest.auth_header)

        self.assertEquals(response.status_int, 200)
        self.assertEquals(response.json['id'], 1)
        from_db = models.Registration.get(models.Registration.id == 1)
        self.assertIsNotNone(from_db)
        self.assertEquals(from_db.topic, topic)

    def test_create_registration_already_exists(self):
        topic = 'test'
        container = 'some_container'
        models.Registration(topic=topic, container=container, creator=RegistrationTest.test_user).save()
        response = test_app.post_json('/registration', {
            'topic': topic,
            'container': container
        }, expect_errors=True, headers=RegistrationTest.auth_header)

        self.assertEquals(response.status_int, 400)

    def test_create_registration_with_different_container(self):
        topic = 'test'
        container = 'some_container'
        diff_container = 'some_other_container'
        models.Registration(topic=topic, container=container, creator=RegistrationTest.test_user).save()
        response = test_app.post_json('/registration', {
            'topic': topic,
            'container': diff_container
        }, expect_errors=True, headers=RegistrationTest.auth_header)

        self.assertEquals(response.status_int, 200)
        self.assertEquals(response.json['id'], 2)
        from_db = models.Registration.get(models.Registration.id == 2)
        self.assertIsNotNone(from_db)
        self.assertEquals(from_db.container, diff_container)

    def test_get_all_registrations(self):
        models.Registration(topic='topic', container='container', creator=RegistrationTest.test_user).save()
        models.Registration(topic='topic', container='container2', creator=RegistrationTest.test_user).save()

        response = test_app.get('/registration', headers=RegistrationTest.auth_header)

        self.assertEquals(response.status_int, 200)
        self.assertEquals(len(response.json['results']), 2)

    def test_get_all_registrations_empty(self):
        response = test_app.get('/registration', headers=RegistrationTest.auth_header)

        self.assertEquals(response.status_int, 200)
        self.assertEquals(len(response.json['results']), 0)

    def test_delete_registration(self):
        models.Registration(topic='topic', container='container', creator=RegistrationTest.test_user).save()

        response = test_app.delete('/registration/1', headers=RegistrationTest.auth_header)

        self.assertEquals(response.status_int, 200)
        self.assertEquals(response.json['id'], 1)

        had_exception = False
        try:
            models.Registration.get(models.Registration.id == 1)
        except models.Registration.DoesNotExist:
            had_exception = True
        self.assertTrue(had_exception)

    def test_delete_does_not_exist(self):
        response = test_app.delete('/registration/1', expect_errors=True, headers=RegistrationTest.auth_header)
        self.assertEquals(response.status_int, 404)

    def test_get_registration(self):
        models.Registration(topic='topic', container='container', creator=RegistrationTest.test_user).save()
        response = test_app.get('/registration/1', headers=RegistrationTest.auth_header)
        self.assertEquals(response.status_int, 200)
        self.assertEquals(response.json['id'], 1)

    def test_get_registration_missing(self):
        response = test_app.get('/registration/1', expect_errors=True, headers=RegistrationTest.auth_header)
        self.assertEquals(response.status_int, 404)

if __name__ == '__main__':
    unittest.main()