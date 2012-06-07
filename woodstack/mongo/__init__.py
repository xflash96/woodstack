import monkey
from .resources import MongoItem, MongoCollection

from pyramid.events import NewRequest
from pymongo import uri_parser
import mongoengine

def includeme(config):
    settings = config.registry.settings

    config.include('..rest')
    monkey.patch()


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
    # overwrite to celery to use the same conn
    #pcelery.celery.backend._connection = conn
    #pcelery.celery.backend._database = conn['celery']

    config.scan()


def add_db_conn(event):
    settings = event.request.registry.settings
    db_conn = settings['mongodb_conn']
    event.request.db_conn = db_conn

def del_db_conn(event):
    def end_db_request(request):
        request.db_conn.end_request()
    event.request.add_finished_callback(end_db_request)
