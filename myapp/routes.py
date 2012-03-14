from resources import PostFactory
#from restview import RESTItemView, RESTSetView

def rest_pair(config, name, factory):
    config.add_route(name+'s', '/'+name+'/', factory=factory, use_global_views=True)
    config.add_route(name, '/'+name+'/{key}', factory=factory, traverse='{key}', use_global_views=True)

def config_routes(config):
    config.add_route('default', '/')
    config.add_route('static', '/static')
    config.add_route('favicon', '/favicon.ico')
    config.add_route('robots', '/robots.txt')
    config.add_static_view('static', 'myapp:static', cache_max_age=0)

    rest_pair(config, 'post', PostFactory)
