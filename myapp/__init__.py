from pyramid.config import Configurator
from myapp.resources import Root

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    config.add_view('myapp.views.my_view',
                    context='myapp:resources.Root',
                    renderer='myapp:templates/mytemplate.pt')
    config.add_static_view('static', 'myapp:static', cache_max_age=3600)
    return config.make_wsgi_app()
