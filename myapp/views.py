from pyramid.view import view_config
import os
from pyramid.response import FileResponse, Response

@view_config(route_name='default', renderer='myapp:templates/main.pt')
def default_view(request):
    return {}

@view_config(route_name='favicon')
def favicon_view(request):
    icon = os.path.dirname(__file__)+'/static/favicon.ico'
    return FileResponse(icon, request=request)

@view_config(route_name='robots')
def robots_view(request):
    txt = os.path.dirname(__file__)+'/static/robots.txt'
    return FileResponse(txt, request=request)

@view_config(route_name='memory')
def memroy_view(request):
    import tasks
    r = tasks.get_memory_usage.delay()
    r.wait()
    return Response(r.result)
