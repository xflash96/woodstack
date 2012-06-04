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

