import unittest

from pyramid import testing

if 1:
    class ViewTests(unittest.TestCase):
        def setUp(self):
            self.config = testing.setUp()

        def tearDown(self):
            testing.tearDown()

        def test_my_view(self):
            from myapp.views import default_view
            request = testing.DummyRequest()
            info = default_view(request)
            self.assertEqual(info['project'], 'myapp')

if 0:
    class IntegrationTest(unittest.TestCase):
        def setUp(self):
            from myapp import main
            from webtest import TestApp
            settings = {
                    'mongodb.uri': 'mongodb://127.0.0.1:44184',
                    'mongodb.db_name': 'xflash96',
                    'celery.broker_url': 'mongodb://localhost:44184',
                    'celery.dbname': 'celery'
                    }
            self.app = TestApp(main({}, **settings))

        def tearDown(self):
            testing.tearDown();

        def test_root(self):
            res = self.app.get('/morph')
            print res
