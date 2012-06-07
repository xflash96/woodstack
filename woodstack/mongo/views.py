from pyramid.view import view_config
from .resources import MongoSON

@view_config(context=MongoSON, renderer='ujson')
def SimpleResponse(request):
    return request.context.son
