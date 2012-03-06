from pyramid.config import Configurator
from pyramid.events import subscriber
from pyramid.events import NewRequest
from pyramid.renderers import JSONP
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
# from myapp.resources import Root
from mongoengine import connect

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    authentication_policy = AuthTktAuthenticationPolicy('secret')
    authorization_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings,
            authentication_policy=authentication_policy,
            authorization_policy=authorization_policy)
    config.add_renderer('jsonp', JSONP(param_name='callback'))
    config.add_route('default', '/')
    config.add_route('data', '/d/*traverse', factory='myapp.resources.Root')
    config.add_route('static', '/static')
    config.add_route('favicon', '/favicon.ico')
    config.add_route('robots', '/robots.txt')
    config.add_static_view('static', 'myapp:static', cache_max_age=0)
    config.scan('myapp')

    # MongoDB
    db_name = settings['mongodb.db_name']
    db_host = settings['mongodb.host']
    db_port = int(settings['mongodb.port'])
    db_user = settings['mongodb.user']
    db_password = settings['mongodb.password']
    if db_user == '':
        db_user = None
        db_password = None
    conn = connect(db_name, username=db_user, password=db_password, 
            host=db_host, port=db_port)
    config.registry.settings['mongodb_conn'] = conn
    config.add_subscriber(add_mongo_db, NewRequest)

    return config.make_wsgi_app()

def add_mongo_db(event):
    settings = event.request.registry.settings
    db_name = settings['mongodb.db_name']
    db = settings['mongodb_conn'][db_name]
    event.request.db = db
