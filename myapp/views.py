from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound, HTTPCreated, HTTPAccepted, HTTPBadRequest
from pyramid.response import Response
from mongoengine import ValidationError
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

def context_to_json(context):
    c = context.to_mongo()
    c.pop('_types')
    c.pop('_cls')
    c['_id'] = str(c['_id'])
    return c

def to_uri(li, request):
    base_uri = request.current_route_url()
    return [base_uri+i.pk for i in li]

def create_or_update(context, request):
    try:
        print request.json_body
        for (k,v) in request.json_body.items():
            setattr(context, k, v)
        if context.__name__ is None:
            context.__name__ = context.pk
        elif context.__name__ != context.pk:
            raise ValueError(context.__name__+' != '+context.pk)
        context.save()
    except (AttributeError, ValueError, ValidationError) as e:
        print str(e)
        return HTTPBadRequest()

@view_config(route_name='data', renderer='json')
def rest_view(context, request):
    ''' handle RESTful request with
                    collection      item
            GET:    list            retrieve
            POST:   new member      new member     -> update if existed
            PUT:    replace whole   replace/create
            DELETE: delete          delete
    '''
    is_collection = request.path_url.endswith('/')
    created = hasattr(context, 'pk')

    print request.method
    if request.method == 'GET':
        if is_collection:
            try:
                limit = int(request.params.get('limit', 16))
                return to_uri(context[:limit], request)
            except ValueError:
                return HTTPBadRequest('Bad limit value')
        else:
            if not created:
                return HTTPNotFound('Items not found')
            else:
                return context_to_json(context)

    elif request.method == 'POST':
        key = None
        try:
            member = context[key]
        except (AttributeError, KeyError): # do not allow create member
            return HTTPNotFound('Not allowed to create member')
        r = create_or_update(member, request)
        if r: # Error happens
            return r
        else:
            return HTTPCreated()

    elif request.method == 'PUT':
        if is_collection:
            raise NotImplementedError('Do not allow drop of collection')
            r = None
        else:
            r = create_or_update(context, request)

        if r:
            return r
        else:
            return HTTPAccepted()

    elif request.method == 'DELETE':
        if is_collection:
            key = None
            try:
                member = context[key]
            except (KeyError, AttributeError): # do not allow create member
                return HTTPNotFound('No members to delete')
            member.drop_collection()
            return HTTPAccepted()    
        else:
            if not created:
                return HTTPNotFound()
            context.delete()
            return HTTPAccepted()

    else:
        raise NotImplementedError('called with '+request.method)



#@view_config(route_name='data', context='myapp.resources.PostAttach', renderer='json')
