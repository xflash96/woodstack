import ujson

def ujson_renderer_factory(info):
    def _renderer(value, system):
        request = system.get('request')
        if request is not None:
            response = request.response
            ct = response.content_type
            if ct == response.default_content_type:
                response.content_type = 'application/json'
        return ujson.dumps(value, ensure_ascii=False, double_precision=6)
    return _renderer
