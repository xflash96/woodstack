from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound

@view_config(route_name='default', renderer='myapp:templates/mytemplate.pt')
def my_view(request):
    return {'project':'myapp'}

@view_config(route_name='data', renderer='json')
def data_fallback(context, request):
    print 'converted'
    if context == None:
        return HTTPNotFound()
    else:
        return context

#@view_config(route_name='data', context='myapp.resources.PostAttach', renderer='json')
