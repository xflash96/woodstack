from mongoengine import Document, StringField, DateTimeField
import datetime
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow, Everyone
from celery import states
import pcelery

'''
Wrapping the mongoengine.Document.
By the constrain in key matching, traversal will not go further level,
and the __getitem__ of context will never be used. (safe!)
'''
class DocFactory(object):
    def __init__(self, request):
        self.request = request
    def __getitem__(self, key):
        q = self.context.objects(pk=key)
        r = q.first()
        if r is None:
            raise KeyError
        else:
            return r
    context = None

class Post(Document):
    key = StringField(max_length=30, primary_key=True)
    title = StringField(max_length = 120, required=True)
    date = DateTimeField(default=datetime.datetime.utcnow, required=True)
    content = StringField(default=lambda : '', required=True)
    @property
    def __acl__(self):
        return [
                (Allow, Everyone, ALL_PERMISSIONS), 
        ]
class PostFactory(DocFactory):
    context = Post
    @property
    def __acl__(self):
        return [
                (Allow, Everyone, ALL_PERMISSIONS), 
        ]

class TaskMeta(object):
    @property
    def __acl__(self):
        return [
                (Allow, Everyone, ALL_PERMISSIONS), 
        ]

class TaskFactory(object):
    context = TaskMeta

    def __init__(self, request):
        self.request = request
        backend = pcelery.celery.backend
        db = backend._get_database()
        self.collection = db[backend.mongodb_taskmeta_collection]

    def __getitem__(self, key):
        r = pcelery.celery.AsyncResult(key)
        t = TaskMeta()
        t.result = r
        return t

    def regular(self):
        d = pcelery.celery.tasks.regular()
        return d

    def periodic(self):
        return pcelery.celery.tasks.periodic()

    def discard_all(self):
        return pcelery.celery.control.discard_all()

    def all_id(self):
        return self.collection.find(fields=['task_id'])

    def all_id_by_name(self, task_name):
        return self.collection.find({'task_name': task_name}, fields=['task_id'])

    @property
    def __acl__(self):
        return [
                (Allow, Everyone, ALL_PERMISSIONS), 
        ]
