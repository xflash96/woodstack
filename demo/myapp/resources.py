from mongoengine import StringField, DateTimeField, ListField, IntField
from mongoengine import EmbeddedDocumentField, EmbeddedDocument, Document
#from mongoengine import FileField, ListField, ObjectIdField
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow, Everyone
from woodstack.mongo import MongoItem, MongoCollection

import datetime


ALLOW_ALL = [(Allow, Everyone, ALL_PERMISSIONS)]

class MetaData(EmbeddedDocument):
    tags = ListField(StringField())
    revisions = ListField(IntField())

class Post(Document):
    key     = StringField   (max_length=30, primary_key=True)
    title   = StringField   (max_length = 120, required=True)
    date    = DateTimeField (default=datetime.datetime.utcnow, required=True)
    content = StringField   (default=lambda : '', required=True)
    metadata = EmbeddedDocumentField(MetaData)

class PostItem(MongoItem):
    doc_class = Post
    @property
    def __acl__(self):
        return ALLOW_ALL
class PostCollection(MongoCollection):
    item_class = PostItem
    @property
    def __acl__(self):
        return ALLOW_ALL
