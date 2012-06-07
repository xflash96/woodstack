from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPCreated, HTTPOk, HTTPBadRequest
from pyramid.httpexceptions import HTTPConflict
from pyramid.response import Response
from .resources import RestItem, RestCollection

import ujson

''' handle RESTful request with

                RESTSetView     RESTItemView

        GET:    list            retrieve
        POST:   add items       partially update attr
        PUT:    Not Impl.       replace item
        DELETE: delete set      delete item
'''

@view_defaults(context=RestItem, renderer='ujson')
class RESTItemView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context
        self.params, self.payload = split_params_and_payload(request)
        self.field = request.matchdict.get('field')

        # specific field_name

    @view_config(request_method='GET', permission='read')
    def get(self):
        '''
        retrieve item content
        '''
        if self.field:
            return self.context.read(field=self.field)
        else:
            return self.context.read()

    @view_config(request_method='POST', permission='update')
    def post(self):
        '''
        partially update item attribute
        '''
        if not self.payload or not isinstance(self.payload, dict):
            return HTTPBadRequest()

        try:
            self.context.update(self.payload)
        except AttributeError:
            return HTTPBadRequest()

        return HTTPOk()

    @view_config(request_method='PUT', permission='update')
    def put(self):
        '''
        replace the item
        '''
        if self.field or not isinstance(self.payload, dict):
            return HTTPBadRequest()

        self.context.update(replace=True)

        return HTTPOk()

    @view_config(request_method='DELETE', permission='delete')
    def delete(self):
        '''
        delete item
        '''
        if self.field:
            return HTTPBadRequest()

        self.context.delete()

        return HTTPOk()

@view_defaults(context=RestCollection, renderer='ujson')
class RESTSetView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context
        self.params, self.payload = split_params_and_payload(request)
        
    @view_config(request_method='GET', permission='read')
    def get(self):
        '''
        list a set of items
        '''
        try:
            limit = int(self.params.get('limit', 16))
            start = int(self.params.get('start', 0))
            return_in_url = 'url' in self.payload
        except ValueError:
            return HTTPBadRequest('Bad Limit Value')

        fields = self.request.params.get('fields')
        if isinstance(fields, basestring) :
            fields = fields.strip().split(',')
            if '_id' not in fields and False:
                fields.append('_id')
        else:
            fields = []

        if return_in_url :
            base_url = self.request.current_route_url()
            return [ base_url+str(i['_id']) for i in 
                    self.context.list(fields=fields, start=start, limit=limit) ]
        else:
            try:
                return self.context.list(fields=fields, start=start, limit=limit)
            except AttributeError:
                return HTTPBadRequest('Fields not found')

    @view_config(request_method='POST', permission='create')
    def post(self):
        '''
        add new member item(s)
        '''
        # add list of items
        if type(self.payload) is list or type(self.payload) is dict:
            if len(self.payload) == 0:
                return HTTPBadRequest()

            try:
                self.context.create(self.payload)
                return HTTPCreated()
            except KeyError:
                return HTTPConflict()

        else:
            return HTTPBadRequest()

    @view_config(request_method='PUT', permission='create')
    def put(self):
        return HTTPBadRequest() #simply not support.

    @view_config(request_method='DELETE', permission='delete')
    def delete(self):
        self.context.drop()
        return HTTPOk()

def split_params_and_payload(req):
    params = {}
    payload = {}

    if  req.content_type.lower() == 'application/json':
        body = req.body
        payload = ujson.loads(body) if body else {}
    elif req.method.upper() == "POST":
        payload = dict(req.POST)
    else:
        params = dict(req.GET)

    return params, payload

@view_config(context=NotImplementedError)
def NotImplView(exc, request):
    response = Response('This feature is not implemented\n'+exc.msg)
    response.status_int = 404
    return response
@view_config(context=Response)
def SimpleResponse(request):
    return request.context
