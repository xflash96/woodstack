from pyramid.security import Allow, Everyone
from pyramid.security import ALL_PERMISSIONS

import pcelery
import datetime
from ..rest import RestItem, RestCollection

ALLOW_ALL = [(Allow, Everyone, ALL_PERMISSIONS)]

class TaskItem(RestItem):
    def read(self):
        meta = self.result.backend.get_task_meta(self.result.task_id)
        date_done = meta.get('date_done')
        if type(date_done) is datetime:
            meta['date_done'] = date_done.isoformat()
        return meta
    def delete(self):
        self.result.forget()
    @property
    def __acl__(self):
        return ALLOW_ALL
    def __init__(self, request, context):
        self.context = context
        self.resut = self.context.result

class TaskCollection(RestCollection):
    item_class = TaskItem

    def __init__(self, request):
        self.request = request
        backend = pcelery.celery.backend
        db = backend._get_database()
        self.collection = db[backend.mongodb_taskmeta_collection]

    def regular(self):
        d = pcelery.celery.tasks.regular()
        return d

    def periodic(self):
        return pcelery.celery.tasks.periodic()

    def drop(self):
        return pcelery.celery.control.discard_all()

    def list(self, fields, start, limit):
        return self.collection.find(fields=['task_id'])

    def __getitem__(self, key):
        result = pcelery.celery.AsyncResult(key)
        t = self.item_class(self.request, result)
        return t

    @property
    def __acl__(self):
        return ALLOW_ALL
