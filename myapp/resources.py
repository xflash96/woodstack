from mongoengine import Document
from mongoengine import StringField
class Root(object):
    def __init__(self, request):
        self.request = request
    def __getitem__(self, key):
        p = Post.objects(key=key).first()
        return p

class Post(Document):
    key = StringField(max_length=30, required=True)
    title = StringField(max_length = 120, required=True)
