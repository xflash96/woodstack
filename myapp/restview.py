from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPCreated, HTTPAccepted, HTTPBadRequest
from mongoengine import ValidationError
from resources import DocFactory
from mongoengine import Document
from datetime import datetime
'''
Convert mongoengine fileds to json
should be a mongoengine.BaseDocument method
'''
def to_python(doc):
    data = {}
    handlers = {
            datetime: lambda x: x.isoformat(),
            }
    for field_name, field in doc._fields.items():
        value = getattr(doc, field_name, None)
        if value is not None:
            value = field.to_python(value)
            h = handlers.get(value.__class__)
            if h is not None:
                value = h(value)
            data[field.db_field] = value

    return data

def to_uri(li, request):
    base_uri = request.current_route_url()
    return [base_uri+i._id for i in li]

def create_or_update(context, request):
    try:
        print request.json_body
        for (k,v) in request.json_body.items():
            setattr(context, k, v)
        if context.__name__ is None:
            context.__name__ = context._id
        elif context.__name__ != context._id:
            raise ValueError(context.__name__+' != '+context._id)
        context.save()
    except (AttributeError, ValueError, ValidationError) as e:
        print str(e)
        return HTTPBadRequest()


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

    @view_config(request_method='GET', permission='read')
    def get(self):
        return to_python(self.context)

    @view_config(request_method='POST', permission='write')
    def post(self):
        for (k,v) in self.request.json_body.iteritems():
            setattr(self.context, k, v)
        self.context.save()
        return HTTPAccepted()

    @view_config(request_method='PUT', permission='write')
    def put(self):
        id_field = self._meta['id_field']
        json_body = self.request.json_body
        if json_body.get(id_field) != getattr(self.context, id_field):
            return HTTPBadRequest()
        n = self.context.__class__(**json_body)
        n.save()
        return HTTPAccepted()

    @view_config(request_method='DELETE', permission='delete')
    def delete(self, request):
        self.context.delete()
        return HTTPAccepted()

@view_defaults(context=DocFactory, renderer='json')
class RESTSetView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context
        print 'set'
        
    @view_config(request_method='GET', permission='list')
    def get(self):
        try:
            limit = int(self.request.params.get('limit', 16))
            return to_uri(self.context.context.objects[:limit], self.request)
        except ValueError:
            return HTTPBadRequest('Bad Limit Value')
        except KeyError:
            return HTTPBadRequest('Empty Set')
    @view_config(request_method='POST', permission='create')
    def post(self):
        json_body = self.request.json_body
        n = self.context.context(**json_body)
        n.save()
        return HTTPCreated()
    @view_config(request_method='PUT', permission='write')
    def put(self):
        raise NotImplementedError('Do not allow replace of collection')
    @view_config(request_method='DELETE', permission='delete')
    def delete(self):
        self.context.context.drop_collection()
        return HTTPAccepted()
