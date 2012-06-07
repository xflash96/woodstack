from pyramid.response import Response
from pyramid.view import view_config

@view_config(context=Response)
def SimpleResponse(request):
    return request.context
