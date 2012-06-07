from myapp.resources import PostCollection
from woodstack.task import TaskCollection

def config_routes(config):
    config.add_route('favicon.ico', '/favicon.ico')
    config.add_route('robots.txt', '/robots.txt')
    config.add_route('humans.txt', '/humans.txt')
    config.add_route('crossdomain.xml', '/crossdomain.xml')
    config.add_route('static', '/static')
    config.add_static_view('static', 'myapp:static', cache_max_age=3600)

    config.add_route('default', '/')
    config.add_rest_route('post', PostCollection)
    config.add_rest_route('task', TaskCollection)

def includeme(config):
    config_routes(config)
