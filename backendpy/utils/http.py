import urllib.parse
import http.client
from typing import Optional

from .json import to_json, from_json


class Client:
    def __init__(
            self,
            base_url: str,
            port: Optional[int] = None,
            ssl: Optional[bool] = False,
            timeout: int = 10):
        self._base_url = base_url
        self._port = port
        self._ssl = ssl
        self._timeout = timeout
        self._session = None

    def __enter__(self):
        self._session = http.client.HTTPSConnection(
            host=self._base_url, port=self._port if self._port is not None else 443, timeout=self._timeout) \
            if self._ssl else http.client.HTTPConnection(
            host=self._base_url, port=self._port if self._port is not None else 80, timeout=self._timeout)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            self._session.close()

    def _prepare_data(self, form=None, json=None, headers=None):
        if not headers:
            headers = dict()
        if json is not None:
            body = to_json(json)
            headers.setdefault('Content-type', 'application/json')
            headers.setdefault('Accept', 'application/json')
        elif form is not None:
            body = urllib.parse.urlencode(form)
            headers.setdefault('Content-type', 'application/x-www-form-urlencoded')
            headers.setdefault('Accept', 'text/plain')
        else:
            body = ''
        return body, headers

    def get(self,
            url: str,
            headers: Optional[dict] = None):
        if self._session:
            self._session.request(method='GET', url=url, headers=headers if headers else dict())
            return Response(self._session.getresponse())

    def post(self,
             url: str,
             form: Optional[dict] = None,
             json: Optional[dict] = None,
             headers: Optional[dict] = None):
        if self._session:
            body, headers = self._prepare_data(form, json, headers)
            self._session.request(method='POST', url=url, body=body, headers=headers)
            return Response(self._session.getresponse())

    def put(self,
            url: str,
            form: Optional[dict] = None,
            json: Optional[dict] = None,
            headers: Optional[dict] = None):
        if self._session:
            body, headers = self._prepare_data(form, json, headers)
            self._session.request(method='PUT', url=url, body=body, headers=headers)
            return Response(self._session.getresponse())

    def patch(self,
              url: str,
              form: Optional[dict] = None,
              json: Optional[dict] = None,
              headers: Optional[dict] = None):
        if self._session:
            body, headers = self._prepare_data(form, json, headers)
            self._session.request(method='PATCH', url=url, body=body, headers=headers)
            return Response(self._session.getresponse())

    def delete(self,
               url: str,
               form: Optional[dict] = None,
               json: Optional[dict] = None,
               headers: Optional[dict] = None):
        if self._session:
            body, headers = self._prepare_data(form, json, headers)
            self._session.request(method='DELETE', url=url, body=body, headers=headers)
            return Response(self._session.getresponse())

    def options(self,
                url: str,
                headers: Optional[dict] = None):
        if self._session:
            self._session.request(method='OPTIONS', url=url, headers=headers if headers else dict())
            return Response(self._session.getresponse())

    def head(self,
             url: str,
             headers: Optional[dict] = None):
        if self._session:
            self._session.request(method='HEAD', url=url, headers=headers if headers else dict())
            return Response(self._session.getresponse())


class Response:
    def __init__(self, r: http.client.HTTPResponse):
        self.headers = dict(r.getheaders())
        self.status = r.status
        self.reason = r.reason
        self.message = r.msg
        self.version = r.version
        self.data = r.read()
        if self.headers.get('content-type') == 'application/json':
            self.data = from_json(self.data)
