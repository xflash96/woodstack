class RestItem(object):
    def update(self, d, replace):
        '''
        Partially update property.
        If replace is True, replace whole property.
        '''
        raise NotImplementedError
    def read(self):
        '''
        Return the dict form of context with specified field.
        If field is [], return all the field.
        '''
        raise NotImplementedError
    def delete(self):
        '''
        Delete the entity.
        '''
        raise NotImplementedError

class RestCollection(object):
    def create(self, d):
        '''
        Create a item by dict d
        '''
        raise NotImplementedError
    def list(self, fields, start, limit):
        '''
        Return a list of dict with specified fields from start to start+limit.
        '''
        raise NotImplementedError
    def drop(self):
        '''
        drop whole collection
        '''
        raise NotImplementedError
    def __getitem__(self, key):
        '''
        Return one RestItem with matched primary key.
        '''
        raise NotImplementedError
