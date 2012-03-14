from mongoengine import Document, StringField, DateTimeField
import datetime
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow, Everyone

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
