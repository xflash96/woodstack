import unittest

from pyramid import testing

if 0:
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
                    'mongodb.uri': 'mongodb://127.0.0.1:44183',
                    'mongodb.db_name': 'xflash96',
                    'celery.broker_url': 'mongodb://localhost:44183',
                    'celery.dbname': 'celery'
                    }
            self.app = TestApp(main({}, **settings))

        def tearDown(self):
            testing.tearDown();

        def test_root(self):
            res = self.app.get('/')
            print res

if __name__ == '__main__':
    import urllib2
    import json

    def json_dial(url, method='GET', d=None):
        headers = {
                "Content-Type":"application/json",
                "X-Requested-With": "XMLHttpRequest",
                } 
        s = json.dumps(d)
        request = urllib2.Request(url, s)
        request.get_method = lambda: method
        for (k,v) in headers.items():
            request.add_header(k,v)
        response = urllib2.urlopen(request)
        print response.info().headers
        return response.read()

    def json_test(url, method, d, expect_code):
        try:
            json_dial(url, method, d)
        except urllib2.HTTPError, e:
            if e.getcode() != expect_code:
                raise e

    d = lambda i: {'title': 'i love '+chr(i)+" kerker", 'key':chr(i), 'content':'contemplating on the meaning of "%d"'%i, 'metadata': {'tags':['stupid'], 'revisions': [1]}}
    l = [d(i) for i in range(ord('a'), ord('z'))]

    url = 'http://127.0.0.1:33123/post'

    json_test(url, 'DELETE', None, 200)
    json_test(url, 'POST', l, 200)
    import sys
    sys.exit(0)
    json_test(url, 'POST', d(ord('A')), 200)
    json_test(url+'/a', 'DELETE', None, 200)

    json_test(url+'/a', 'DELETE', None, 404)
    json_test(url, 'POST', d(ord('A')), 409)

    l = l[:len(l)/2]
    json_test(url, 'POST', l, 409)

    json_test(url, 'DELETE', None, 200)
