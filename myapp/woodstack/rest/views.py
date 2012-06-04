from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPCreated, HTTPOk, HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound, HTTPConflict
from pyramid.response import Response, FileResponse

from mongoengine import ValidationError, InvalidQueryError, OperationError
from mongoengine import Document, FileField
from pymongo.connection import DuplicateKeyError

from resources import DocFactory

import ujson
from datetime import datetime

''' handle RESTful request with

                RESTSetView     RESTItemView

        GET:    list            retrieve
        POST:   add items       partially update attr
        PUT:    Not Impl.       replace item
        DELETE: delete set      delete item
'''

@view_defaults(context=Document, renderer='ujson')
class RESTItemView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context
        self.id_field = request.context._meta['id_field']

        self.params, self.files, self.payload = split_params_files_payload(request)
        # specific field_name
        field_name  = request.matchdict.get('field_name')
        self.field = getattr(request.context, field_name, None) if field_name else None

    @view_config(request_method='GET', permission='view')
    def get(self):
        '''
        retrieve item content
        '''
        if self.field:
            if type(self.field) is not FileField:
                return HTTPBadRequest()

            grid_file = self.field.get()
            if not grid_file:
                return HTTPNotFound()

            return FileResponse(file_obj=grid_file, last_modified=grid_file.upload_date)
        else:
            return document_to_python(self.request, self.context)

    @view_config(request_method='POST', permission='edit')
    def post(self):
        '''
        partially update item attribute
        '''
        if self.field or not isinstance(self.payload, dict):
            return HTTPBadRequest()

        # do not change existed id
        if self.id_field in self.payload:
            self.payload.pop(self.id_field)

        for (k,v) in self.payload.iteritems():
            if hasattr(self.context, k):
                setattr(self.context, k, v)
        self.context.save(validate=True, safe=True)
        return HTTPOk()

    @view_config(request_method='PUT', permission='edit')
    def put(self):
        '''
        replace the whole item
        '''
        if self.field or not isinstance(self.payload, dict):
            return HTTPBadRequest()
        elif self.id_field in self.payload:
            return HTTPBadRequest()

        self.payload[self.id_field] = self.context._id
        n = self.context.__class__(**self.payload)
        n.save(validate=True, safe=True)

        return HTTPOk()

    @view_config(request_method='DELETE', permission='delete')
    def delete(self):
        if self.field:
            return HTTPBadRequest()
        doc = self.context
        for field_name, field in doc._fields.iteritems():
            # cascade delete FileField, this will be in mongoengine in the future
            if type(field) is FileField:
                value = getattr(doc, field_name, None)
                value.delete()
        self.context.delete()
        return HTTPOk()

@view_defaults(context=DocFactory, renderer='ujson')
class RESTSetView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context.context
        self.params, self.files, self.payload = split_params_files_payload(request)
        
    @view_config(request_method='GET', permission='list')
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
        self.id_field = self.context._meta['id_field']
        if isinstance(fields, basestring) :
            fields = fields.strip().split(',')
            if self.id_field not in fields:
                fields.append(self.id_field)
        else:
            fields = []

        if return_in_url :
            base_url = self.request.current_route_url()
            return [ base_url+str(i._id)
                     for i in self.context.objects\
                        .only(self.id_field)[start:start+limit] ]
        else:
            try:
                q = self.context.objects.only(*fields)[start:start+limit]
                return [document_to_python(self.request, i, fields) for i in q]
            except InvalidQueryError:
                return HTTPBadRequest('Fields not found')

    def create_new_item(self, d):
        n = self.context(**d)
        for k,v in self.files.iteritems():
            if hasattr(n, k):
                field = getattr(n, k)
                field.put(v.file, filename=v.filename)
        return n

    @view_config(request_method='POST', permission='create')
    def post(self):
        '''
        add new member item(s)
        '''
        # add list of items
        if isinstance(self.payload, list):
            if len(self.payload) == 0:
                return HTTPBadRequest()

            to_add = []
            for i in self.payload:
                n = self.create_new_item(i)
                n.validate()
                to_add.append(n)
            try:
                self.context.objects.insert(to_add, load_bulk=True)
                return HTTPCreated()
            except DuplicateKeyError:
                return HTTPConflict()

        # add a single item
        elif isinstance(self.payload, dict):
            try:
                n = self.create_new_item(self.payload)
                try:
                    n.save(safe=True, force_insert=True)
                except OperationError, e:
                    if 'duplicate key' in unicode(e):
                        # common... plz expose the DuplicateKeyError
                        return HTTPConflict()
                    else:
                        raise e
                return HTTPCreated()
            except DuplicateKeyError:
                return HTTPConflict()
        else:
            return HTTPBadRequest()

    @view_config(request_method='PUT', permission='edit')
    def put(self):
        return HTTPBadRequest() #simply not support.

    @view_config(request_method='DELETE', permission='drop')
    def delete(self):
        doc = self.context

        # find all files, including list of files
        file_fields = []
        for field_name, field in doc._fields.iteritems():
            if hasattr(field, 'proxy_class'):
                file_fields.append(field_name)
            elif hasattr(field, 'field'):
                list_field = getattr(field, 'field')
                if hasattr(list_field, 'proxy_class'):
                    file_fields.append(field_name)

        if file_fields:
            q = self.context.objects.only(*file_fields)
            for i in q:
                for field_name in file_fields:
                    field = getattr(i, field_name)
                    if hasattr(field, 'delete'):
                        field.delete()
                    else: #list
                        for j in field:
                            j.delete()
        self.context.drop_collection()
        return HTTPOk()

@view_config(context=NotImplementedError)
def NotImplView(exc, request):
    response = Response('This feature is not implemented\n'+exc.msg)
    response.status_int = 404
    return response

@view_config(context=ValidationError)
def ValidErrView(exc, request):
    return HTTPBadRequest('Validation Error')

from mongoengine.fields import ObjectId, GridFSProxy
def field_to_json(field_name, value, prefix_url=None):
    if prefix_url is not None:
        ref_url = '/'.join([prefix_url, field_name])
    handlers = {
            datetime: lambda v: v.isoformat(),
            ObjectId: lambda v: str(v),
            GridFSProxy: lambda v: ref_url,
            }
    h = handlers.get(value.__class__)
    if not h:
        return value
    else:
        return h(value)

def document_to_python(request, doc, fields=[]):
    prefix_url = request.current_route_url().rstrip('/')
    if isinstance(request.context, DocFactory): # path to collection
        id_field = doc._meta['id_field']
        prefix_url = '/'.join([prefix_url, field_to_json(id_field, doc._id)])
    #FIXME setview of item file url not correct
    data = {}

    if fields != []:
        clean_fields = {}
        for f in fields:
            clean_fields[f] = doc._fields[f]
    else:
        clean_fields = doc._fields

    for field_name, field in clean_fields.items():
        value = getattr(doc, field_name, None)
        if value is not None:
            value = field.to_python(value)
            value = field_to_json(field_name, value, prefix_url)
            data[field_name] = value

    return data

def split_params_files_payload(request):
    params = {}
    files = {}
    payload = {}

    ct = request.content_type.lower() 
    if ct == 'multipart/form-data':
        for k,v in request.params.iteritems():
            if hasattr(v, 'file'):
                files[k] = v
            else:
                params[k] = v
    elif ct == 'application/json':
        body = request.body
        payload = ujson.loads(body) if body else None
    else:
        params = dict(request.params)

    return params, files, payload
