from pyramid.view import view_config
import os
from pyramid.response import FileResponse, Response

@view_config(route_name='default', renderer='myapp:templates/main.pt')
def default_view(request):
    return {}

_here = os.path.dirname(__file__)
_cache_max_age = 3600

# FIXME I'm not sure file iterator will work as expected in gevent
_ico = os.path.join(_here, 'static', 'ico', 'favicon.ico')
_ico_resp = FileResponse(_ico, cache_max_age=_cache_max_age)
@view_config(route_name='favicon.ico')
def favicon_view(request):
    return _ico_resp

_robots = os.path.join(_here, 'static', 'robots.txt')
_robots_resp = FileResponse(_robots, cache_max_age=_cache_max_age)
@view_config(route_name='robots.txt')
def robots_view(request):
    return _robots_resp

_humans = os.path.join(_here, 'static', 'humans.txt')
_humans_resp = FileResponse(_humans, cache_max_age=_cache_max_age)
@view_config(route_name='humans.txt')
def humans_view(request):
    return _humans_resp

_crossdomain = os.path.join(_here, 'static', 'crossdomain.xml')
_crossdomain_resp = FileResponse(_crossdomain, cache_max_age=_cache_max_age)
@view_config(route_name='crossdomain.xml')
def crossdomain_view(request):
    return _crossdomain_resp

if 0:
    @view_config(route_name='memory')
    def memroy_view(request):
        import tasks
        r = tasks.get_memory_usage.delay()
        r.wait()
        r = r.result
        return Response(r)
