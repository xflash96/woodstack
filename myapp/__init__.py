import gevent.monkey; gevent.monkey.patch_all()
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

import woodstack.mongo

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    authentication_policy = AuthTktAuthenticationPolicy('sekret')
    authorization_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings,
            authentication_policy=authentication_policy,
            authorization_policy=authorization_policy)

    config.include('myapp.routes')
    config.include('pyramid_sockjs')
    config.include(woodstack.mongo)
    config.scan('myapp')

    return config.make_wsgi_app()
