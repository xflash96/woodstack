from myapp.resources import PostFactory

from woodstack.rest import rest_pair
from woodstack.task import TaskFactory

def config_routes(config):
    config.add_route('favicon.ico', '/favicon.ico')
    config.add_route('robots.txt', '/robots.txt')
    config.add_route('humans.txt', '/humans.txt')
    config.add_route('crossdomain.xml', '/crossdomain.xml')
    config.add_route('static', '/static')
    config.add_static_view('static', 'myapp:static', cache_max_age=3600)

    config.add_route('default', '/')
    rest_pair(config, 'post', PostFactory)
    rest_pair(config, 'task', TaskFactory)

def includeme(config):
    config_routes(config)
