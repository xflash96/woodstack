def rest_pair(config, name, factory):
    config.add_route(name+'_s', '/'+name+'/', factory=factory, use_global_views=True)
    config.add_route(name+'_n', '/'+name, factory=factory, use_global_views=True)
    config.add_route(name+'_i', '/'+name+'/{key}', factory=factory, traverse='{key}', use_global_views=True)
    config.add_route(name+'_f', '/'+name+'/{key}/{field_name}', factory=factory, traverse='{key}', use_global_views=True)

