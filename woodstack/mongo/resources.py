import mongoengine
from mongoengine import ValidationError, InvalidQueryError, OperationError
from mongoengine import FileField
from mongoengine.fields import ObjectId, GridFSProxy
from pymongo.connection import DuplicateKeyError
from pyramid.response import FileResponse
import pymongo.son
import datetime

from ..rest import RestItem, RestCollection

class MongoSON(object):
    son = None
    def __init__(self, d):
        if type(d) is dict:
            self.son = dict(d)
        else:
            self.son = d

    def __getitem__(self, key):
        print type(self.son)
        if type(self.son) is dict:
            d = self.son.__getitem__(key)
        else:
            raise KeyError
        return self.__class__(d)

class MongoItem(RestItem):
    doc_class = mongoengine.Document
    context = None
    def update(self, d, replace=False):
        #FIXME test change of id
        #FIXME ignore replace
        n = self.doc_class(**d)
        try:
            n.save(validate=True, safe=True)
        except ValidationError:
            raise AttributeError

    def read(self):
        return document_to_python(self.context, [], self.request.current_route_url())

    def delete(self):
        doc = self.context
        for field_name, field in doc._fields.iteritems():
            if type(field) is FileField:
                value = getattr(doc, field_name, None)
                value.delete()
        self.context.delete()

    @property
    def __acl__(self):
        raise NotImplementedError
    def __init__(self, request, context):
        self.request = request
        self.context = context
    def __getitem__(self, field_name):
        field = self.doc_class._fields.get(field_name, None)
        if field is None:
            raise KeyError
        elif type(field) is FileField:
            grid_file = self.field.get()
            if not grid_file:
                return KeyError
            return FileResponse(file_obj=grid_file, last_modified=grid_file.upload_date)
        else:
            v = getattr(self.context, field_name)
            v = v.to_mongo()
            del v['_types']
            del v['_cls']
            return MongoSON(v)

class MongoCollection(RestCollection):
    item_class = MongoItem

    def new_item(self, d):
        files = {}
        for k,v in d.iteritems():
            if hasattr(v, 'file'):
                files[k] = v
                del d[k]

        if '_cls' in d:
            del d['_cls']
        son = pymongo.son.SON(d)
        n = self.doc_class._from_son(son)

        for k,v in files:
            if hasattr(n, k):
                field = getattr(n, k)
                field.put(v.file, filename=v.filename)
        return n

    def create(self, d):
        if type(d) is dict:
            n = self.new_item(d)
            try:
                n.save(safe=True, force_insert=True)
            except OperationError, e:
                if 'duplicate key' in unicode(e):
                    # ... plz expose the DuplicateKeyError
                    raise KeyError
                else:
                    raise e
            except ValidationError:
                raise AttributeError

        elif type(d) is list:
            to_add = []
            for i in d:
                n = self.new_item(i)
                try:
                    n.validate()
                except ValidationError, e:
                    print e.errors
                    continue
                to_add.append(n)
            try:
                self.doc_class.objects.insert(to_add, load_bulk=True)
            except DuplicateKeyError:
                raise KeyError
            except ValidationError:
                raise AttributeError

    def list(self, fields, start, limit):
        try:
            l = []
            for i in self.doc_class.objects.only(*fields)[start:start+limit]:
                item_url = self.request.current_route_url()+i._id
                l.append(document_to_python(i, fields, item_url))
            return l
        except InvalidQueryError:
            raise AttributeError

    def drop(self):

        for i in self.doc_class.objects:
            c = self.item_class(self.request, i)
            c.delete()

        self.doc_class.drop_collection()

    @property
    def __acl__(self):
        raise NotImplementedError
    def __init__(self, request):
        self.request = request
        self.doc_class = self.item_class.doc_class
    def __getitem__(self, _id):
        query = self.doc_class.objects(pk=_id)
        result = query.first()
        if result is None:
            raise KeyError
        else:
            return self.item_class(self.request, result)

def field_to_python(field_name, value, prefix_url):
    field_url = '/'.join([prefix_url, field_name])
    handlers = {
            datetime:   lambda v: v.isoformat(),
            ObjectId:   lambda v: str(v),
            GridFSProxy:lambda v: field_url,
            }
    h = handlers.get(value.__class__)
    if not h:
        return value
    else:
        return h(value)

def document_to_python(doc, fields, prefix_url):
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
            value = field_to_python(field_name, value, prefix_url)
            data[field_name] = value

    return data

