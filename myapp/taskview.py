from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPAccepted
from resources import TaskMeta, TaskFactory
from datetime import datetime

@view_defaults(context=TaskMeta, renderer='json')
class TaskItemView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context
        self.result = request.context.result

    @view_config(request_method='GET', permission='view')
    def get(self):
        meta = self.result.backend.get_task_meta(self.result.task_id)
        date_done = meta.get('date_done')
        if type(date_done) is datetime:
            meta['date_done'] = date_done.isoformat()
        return meta

    @view_config(request_method='DELETE', permission='delete')
    def delete(self):
        self.result.forget()
        return HTTPAccepted()

@view_defaults(context=TaskFactory, renderer='json')
class TaskSetView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context
        
    @view_config(request_method='GET', permission='list')
    def get(self):
        task_name = self.request.params.get('task_name')
        limit = int(self.request.params.get('limit', 16))
        if task_name is None:
            q = self.context.all_id().limit(limit)
            r= to_uri(q, self.request)
            return r

        task_name = task_name.strip()
        if task_name == '':
            return {'regular': self.context.regular().keys(),
                    'periodic': self.context.periodic().keys()}
        else:
            q = self.context.all_id_by_name(task_name)
            q = q.limit(limit)
            return to_uri(q, self.request)

    @view_config(request_method='DELETE', permission='drop')
    def delete(self):
        self.context.drop_collection()
        self.discard_all()
        return HTTPAccepted()

def to_uri(li, request):
    base_uri = request.current_route_url()
    return [base_uri+i['_id'] for i in li]
