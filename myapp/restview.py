from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPCreated, HTTPAccepted, HTTPBadRequest
from pyramid.response import Response
from mongoengine import ValidationError, InvalidQueryError
from pymongo.connection import DuplicateKeyError
from resources import DocFactory
from mongoengine import Document
from datetime import datetime
''' handle RESTful request with
                RESTSetView     RESTItemView
        GET:    list            retrieve
        POST:   add new member  update attr
        PUT:    Replace Set     replace item
        DELETE: delete set      delete item
'''

@view_defaults(context=Document, renderer='json')
class RESTItemView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(request_method='GET', permission='view')
    def get(self):
        return to_python(self.context)

    @view_config(request_method='POST', permission='edit')
    def post(self):
        for (k,v) in self.request.json_body.iteritems():
            setattr(self.context, k, v)
        self.context.save()
        return HTTPAccepted()

    @view_config(request_method='PUT', permission='edit')
    def put(self):
        id_field = self._meta['id_field']
        json_body = self.request.json_body
        if json_body.get(id_field) != getattr(self.context, id_field):
            return HTTPBadRequest()
        n = self.context.__class__(**json_body)
        n.save()
        return HTTPAccepted()

    @view_config(request_method='DELETE', permission='delete')
    def delete(self):
        self.context.delete()
        return HTTPAccepted()

@view_defaults(context=DocFactory, renderer='json')
class RESTSetView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context.context
        
    @view_config(request_method='GET', permission='list')
    def get(self):
        try:
            limit = int(self.request.params.get('limit', 16))
            fields = self.request.params.get('fields')
            if fields is None:
                fields = ['pk']
            else:
                fields = fields.strip().split(',')

            if len(fields) == 1 and fields[0]=='pk':
                return to_uri(self.context.objects[:limit], self.request)
            else:
                try:
                    print fields
                    q = self.context.objects.only(*fields)[:limit]
                    return [to_python(i, fields) for i in q]
                except InvalidQueryError:
                    return HTTPBadRequest('fields not found')
#        except ValueError:
 #           return HTTPBadRequest('Bad Limit Value')
        except KeyError:
            return HTTPBadRequest('Empty Set')

    @view_config(request_method='POST', permission='create')
    def post(self):
        json_body = self.request.json_body
        if type(json_body) is dict:
            json_body = [json_body]
        nlist = []
        for i in json_body:
            n = self.context(**i)
            nlist.append(n)
        try:
            ids = self.context.objects.insert(nlist, load_bulk=True)
            urilist = to_uri(ids, self.request)
            return HTTPCreated(urilist)
        except DuplicateKeyError:
            return HTTPBadRequest('Key Duplicated')
    @view_config(request_method='PUT', permission='edit')
    def put(self):
        raise NotImplementedError('Do not allow replace of collection')

    @view_config(request_method='DELETE', permission='drop')
    def delete(self):
        self.context.drop_collection()
        return HTTPAccepted()

@view_config(context=NotImplementedError)
def NotImplView(exc, request):
    response = Response('This feature is not implemented\n'+exc.msg)
    response.status_int = 404
    return response

@view_config(context=ValidationError)
def ValidErrView(exc, request):
    response = Response('Validation Error\n'+exc.msg)
    response.status_int = 404
    return response

'''
Convert mongoengine fileds to json
should be a mongoengine.BaseDocument method
'''
def to_python(doc, fields=None):
    data = {}
    handlers = {
            datetime: lambda x: x.isoformat(),
            }
    d = doc._fields

    if fields is not None:
        clean_fields = {}
        for f in fields:
            clean_fields[f] = d[f]
    else:
        clean_fields = d

    for field_name, field in clean_fields.items():
        value = getattr(doc, field_name, None)
        if value is not None:
            value = field.to_python(value)
            h = handlers.get(value.__class__)
            if h is not None:
                value = h(value)
            data[field_name] = value

    return data

def to_uri(li, request):
    base_uri = request.current_route_url()
    return [base_uri+i._id for i in li]
