from celery import Celery as _Celery
from pymongo import uri_parser
from pyramid.path import caller_package
import venusian
import pkgutil

celery = None
_modules_to_register = set()
_celery_routes = {}


class _Task(object):
    queue = 'celery'
    venusian = venusian
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, wrapped):
        def callback(scanner, name, ob):
            global celery
            task = celery.task(self.wrapped, *self.args, **self.kwargs)
            setattr(info.module, name, task)

        self.wrapped = wrapped
        global _modules_to_register
        global _celery_routes
        wrapped_mod = wrapped.__module__
        wrapped_name = wrapped.__name__
        _modules_to_register.add(wrapped_mod)
        name = self.kwargs.get('name')
        if name is None:
            name = '.'.join([wrapped_mod,wrapped_name])
        _celery_routes[name] = \
                {'queue': self.queue}
        info = self.venusian.attach(wrapped, callback, category='pcelery')
        return wrapped

task = _Task

def scan(scope=None):
    scanner = venusian.Scanner()
    if scope is None:
        scope = caller_package()
    scanner.scan(scope, categories=('pcelery',))

def touch_all_package(package):
    path = package.__path__
    for loader, module_name, is_pkg in  pkgutil.walk_packages(path):
        if is_pkg:
            mod = loader.find_module(module_name)
            mod.load_module(module_name)
            exec('import %s' % module_name)
            
def config_celery(settings, package=None):
    if package is None:
        package = caller_package()
    touch_all_package(package)
    obj_config = config_celery_for_mongo(settings)
    global celery
    celery = _Celery()
    celery.config_from_object(obj_config)
    #print celery.backend
    #print obj_config

def config_celery_for_mongo(settings):
    db_uri = settings['mongodb.uri'].strip('"\'')
    db_name = settings['celery.dbname'].strip('"\'')
    res = uri_parser.parse_uri(db_uri)
    host, port = res['nodelist'][0]
    global _modules_to_register
    global _celery_routes
    print 'collected tasks'
    print _celery_routes.keys()

    celery_config = {
        'CELERY_RESULT_BACKEND' : 'mongodb',
        'BROKER_TRANSPORT'      : 'mongodb',
        'CELERY_IMPORTS': tuple(_modules_to_register),
        'BROKER_HOST'   : host,
        'BROKER_PORT'   : port,
        'BROKER_VHOST'  : db_name,
        'CELERY_MONGODB_BACKEND_SETTINGS' : {
            'host': host,
            'port': port,
            'database': db_name
        },
        'CELERY_DISABLE_RATE_LIMITS': True,
        'CELERY_ROUTES': _celery_routes,
        'CELERYD_POOL': 'gevent',
    }
    return celery_config
