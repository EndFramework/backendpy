from urllib.parse import parse_qs
from email.parser import BytesParser
from .helpers.json import from_json


class Request:
    def __init__(self, app=None, scope=None, body=None, url_vars=None):
        self.app = app
        self.context = {}
        self.method = None
        self.path = None
        self.scheme = None
        self.headers = None
        self.url_vars = url_vars
        self.params = None
        self.json = None
        self.form = None
        self.files = None
        self.cleaned_data = None
        if scope:
            self.apply_scope(scope)
            if body:
                self.apply_body(body)

    def apply_scope(self, scope):
        # self.raw_scope = scope
        self.method = scope['method']
        self.path = scope['path']
        self.scheme = scope['scheme']
        self.headers = {k.decode(): v.decode() for k, v in scope['headers']}
        if scope.get('query_string'):
            self.params = {k: (v[0] if len(v) == 1 else v)
                           for k, v in parse_qs(scope['query_string'].decode('utf8')).items()}

    def apply_body(self, body):
        if self.headers is None:
            raise Exception('request scope is not applied')
        # self.raw_body = body
        if self.headers.get('content-type') == 'application/json':
            self.json = from_json(body)
        elif self.headers.get('content-type') == 'application/x-www-form-urlencoded':
            self.form = {k: (v[0] if len(v) == 1 else v)
                         for k, v in parse_qs(body.decode('utf8')).items()}
        # elif self.headers.get('content-type') == 'application/octet-stream':
        #    self.file = body
        # elif self.headers.get('content-type') == 'text/plain':
        #    self.text = str(body)
        elif self.headers.get('content-type') == 'multipart/form-data':
            json_parts = dict()
            form_parts = dict()
            file_parts = dict()
            # text_parts = dict()
            for part in BytesParser().parsebytes(body).get_payload():
                part_type = part.get_content_type()
                if part_type == 'application/json':
                    json_parts[part.get_param(param='name', header='content-disposition')] = \
                        from_json(part.get_payload())
                elif part_type == 'application/x-www-form-urlencoded':
                    form_parts[part.get_param(param='name', header='content-disposition')] = \
                        {k: (v[0] if len(v) == 1 else v)
                         for k, v in parse_qs(part.get_payload().decode('utf8')).items()}
                elif part_type == 'application/octet-stream':
                    file_parts[part.get_param(param='name', header='content-disposition')] = \
                        {'content': part.get_payload(),
                         'file-name': part.get_param(param='filename', header='content-disposition'),
                         'content-type': part.get_content_subtype()}  # Todo: test
                # elif part_type == 'text/plain':
                #    text_parts[part.get_param(param='name', header='content-disposition')] = \
                #        str(part.get_payload(decode=True))
            if json_parts:
                self.json = json_parts if len(json_parts) > 1 else json_parts[0]
            if form_parts:
                self.form = form_parts if len(form_parts) > 1 else form_parts[0]
            if file_parts:
                self.files = file_parts
            # if text_parts:
            #    self.text = text_parts if len(text_parts) > 1 else text_parts[0]
