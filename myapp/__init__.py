from pyramid.config import Configurator
#from pyramid.events import subscriber
from pyramid.events import NewRequest
from pyramid.renderers import JSONP
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
# from myapp.resources import Root
from routes import config_routes
#import myapp.patch.geventmongo; myapp.patch.geventmongo.patch()
import myapp.patch.mongoengine_bulk; myapp.patch.mongoengine_bulk.patch()
from pymongo import uri_parser
import mongoengine
import pcelery

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    authentication_policy = AuthTktAuthenticationPolicy('secret')
    authorization_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings,
            authentication_policy=authentication_policy,
            authorization_policy=authorization_policy)
    config.add_renderer('jsonp', JSONP(param_name='callback'))

    config_routes(config)

    config.scan('myapp')

    # MongoDB
    db_uri = settings['mongodb.uri']
    db_name = settings['mongodb.db_name']

    # parse before mongoengine changes
    res = uri_parser.parse_uri(db_uri)
    host, port = res['nodelist'][0]
    conn = mongoengine.connect(db_name, host=host, port=port)
    config.registry.settings['mongodb_conn'] = conn
    config.add_subscriber(add_db_conn, NewRequest)
    config.add_subscriber(del_db_conn, NewRequest)
    pcelery.includeme(config)
    pcelery.scan()


    return config.make_wsgi_app()

def add_db_conn(event):
    settings = event.request.registry.settings
    db_conn = settings['mongodb_conn']
    event.request.db_conn = db_conn

def del_db_conn(event):
    def end_db_request(request):
        request.db_conn.end_request()
    event.request.add_finished_callback(end_db_request)
