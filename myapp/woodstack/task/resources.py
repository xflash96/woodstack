from pyramid.security import Allow, Everyone
from pyramid.security import ALL_PERMISSIONS

import pcelery

ALLOW_ALL = [(Allow, Everyone, ALL_PERMISSIONS)]

class TaskMeta(object):
    @property
    def __acl__(self):
        return ALLOW_ALL

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
        return ALLOW_ALL
