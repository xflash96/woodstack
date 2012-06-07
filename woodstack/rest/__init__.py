from .resources import RestItem, RestCollection
from .routes import add_rest_route
from .renderers import ujson_renderer_factory

def includeme(config):
    config.include('..rest')
    config.add_directive('add_rest_route', add_rest_route)
    config.add_renderer('ujson', ujson_renderer_factory)
    config.scan()
