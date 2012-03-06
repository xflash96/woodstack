from mongoengine import Document
from mongoengine import StringField

def get_items(cls, key, parent):
    if type(key) is slice:
        return cls.objects[key]

    p = cls.objects(pk=key).first()
    if p is None:
        #print key, 'not found by get_items'
        p = cls()

    p.__name__ = key
    p.__parent__ = parent
    return p

class Root(object):
    __name__ = None
    __parent__ = None
    def __init__(self, request):
        self.request = request
    def __getitem__(self, key):
        return get_items(Post, key, self)

class Post(Document):
    # if the object is of mongoengine type, we should not use __getitem__ FIXME...
    key = StringField(max_length=30, primary_key=True)
    title = StringField(max_length = 120, required=True)
