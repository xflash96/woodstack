from pyramid.view import view_config
from pyramid.response import Response
import os

#this will be replaced in latest pyramid
#from pyramid.response import FileResponse
def FileResponse(path, request):
    content_type = ''
    if path.endswith('.ico'):
        content_type = 'image/x-icon'
    elif path.endswith('.txt'):
        content_type = 'plain/text'

    f = open(path)
    return Response(content_type=content_type, app_iter=f)

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

