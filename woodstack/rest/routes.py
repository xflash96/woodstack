def add_rest_route(config, prefix, factory):
    route_name = '_REST_'+factory.__name__
    route = ''.join([prefix, '*traverse'])
    config.add_route(route_name, route, factory=factory, use_global_views=True)
