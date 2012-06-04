from mongoengine import Document, StringField, DateTimeField
#from mongoengine import FileField, ListField, ObjectIdField
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow, Everyone

from woodstack.rest import DocFactory

import datetime


ALLOW_ALL = [(Allow, Everyone, ALL_PERMISSIONS)]

class Post(Document):
    key = StringField(max_length=30, primary_key=True)
    title = StringField(max_length = 120, required=True)
    date = DateTimeField(default=datetime.datetime.utcnow, required=True)
    content = StringField(default=lambda : '', required=True)
    @property
    def __acl__(self):
        return ALLOW_ALL
class PostFactory(DocFactory):
    context = Post
    @property
    def __acl__(self):
        return ALLOW_ALL
