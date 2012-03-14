from resources import PostFactory
#from restview import RESTItemView, RESTSetView

def rest_pair(config, name, factory):
    config.add_route(name+'s', '/'+name+'/', factory=factory, use_global_views=True)
    config.add_route(name, '/'+name+'/{key}', factory=factory, traverse='{key}', use_global_views=True)
    #config.add_view(RESTSetView, route_name=name+'s')
    #config.add_view(RESTItemView, route_name=name)

def config_routes(config):
    config.add_route('default', '/')
    rest_pair(config, 'a', PostFactory)
    rest_pair(config, 'b', PostFactory)
    config.add_route('static', '/static')
    config.add_route('favicon', '/favicon.ico')
    config.add_route('robots', '/robots.txt')
    config.add_static_view('static', 'myapp:static', cache_max_age=0)
