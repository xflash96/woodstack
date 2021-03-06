#
# make pyramid.response.FileResponse support input iter
#

import pyramid.response
import mimetypes
from os.path import (
    getmtime,
    getsize,
    )

from webob import Response as _Response
from zope.interface import implementer
from pyramid.interfaces import IResponse

def init_mimetypes(mimetypes):
    # this is a function so it can be unittested
    if hasattr(mimetypes, 'init'):
        mimetypes.init()
        return True
    return False

# See http://bugs.python.org/issue5853 which is a recursion bug
# that seems to effect Python 2.6, Python 2.6.1, and 2.6.2 (a fix
# has been applied on the Python 2 trunk).
init_mimetypes(mimetypes)

_BLOCK_SIZE = 4096 * 64 # 256K

@implementer(IResponse)
class Response(_Response):
    pass

class FileResponse(Response):
    """
    A Response object that can be used to serve a static file from disk
    simply.

    ``path`` is a file path on disk.

    ``request`` must be a Pyramid :term:`request` object if passed.  Note
    that a request *must* be passed if the response is meant to attempt to
    use the ``wsgi.file_wrapper`` feature of the web server that you're using
    to serve your Pyramid application.

    ``cache_max_age`` if passed, is the number of seconds that should be used
    to HTTP cache this response.

    ``content_type``, if passed, is the content_type of the response.

    ``content_encoding``, if passed is the content_encoding of the response.
    It's generally safe to leave this set to ``None`` if you're serving a
    binary file.  This argument will be ignored if you don't also pass
    ``content-type``.
    """
    def __init__(self, path=None, request=None, cache_max_age=None,
                 content_type=None, content_encoding=None, file_obj=None,
                 last_modified=None):
        super(FileResponse, self).__init__(conditional_response=True)
        if last_modified:
            self.last_modified = last_modified
        else:
            self.last_modified = getmtime(path)

        if file_obj:
            path = file_obj.name

        if content_type is None:
            content_type, content_encoding = mimetypes.guess_type(path,
                                                                  strict=False)
        if content_type is None:
            content_type = 'application/octet-stream'
        self.content_type = content_type
        self.content_encoding = content_encoding
        app_iter = None
        if file_obj:
            content_length = file_obj.length
            app_iter = file_obj.__iter__()
        else:
            content_length = getsize(path)
            f = open(path, 'rb')
        if request is not None:
            environ = request.environ
            if 'wsgi.file_wrapper' in environ:
                app_iter = environ['wsgi.file_wrapper'](f, _BLOCK_SIZE)
        if app_iter is None:
            app_iter = FileIter(f, _BLOCK_SIZE)
        self.app_iter = app_iter
        # assignment of content_length must come after assignment of app_iter
        self.content_length = content_length
        if cache_max_age is not None:
            self.cache_expires = cache_max_age

class FileIter(object):
    """ A fixed-block-size iterator for use as a WSGI app_iter.

    ``file`` is a Python file pointer (or at least an object with a ``read``
    method that takes a size hint).

    ``block_size`` is an optional block size for iteration.
    """
    def __init__(self, file, block_size=_BLOCK_SIZE):
        self.file = file
        self.block_size = block_size

    def __iter__(self):
        return self

    def next(self):
        val = self.file.read(self.block_size)
        if not val:
            raise StopIteration
        return val

    __next__ = next # py3

    def close(self):
        self.file.close()

def patch():
    pass
    #pyramid.response.FileResponse = FileResponse
