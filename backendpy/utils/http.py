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

    def _prepare_data(self, form=None, json=None, body=None, headers=None):
        if not headers:
            headers = dict()
        if json is not None:
            data = to_json(json)
            headers.setdefault('content-type', 'application/json')
            headers.setdefault('accept', 'application/json')
        elif form is not None:
            data = urllib.parse.urlencode(form)
            headers.setdefault('content-type', 'application/x-www-form-urlencoded')
            headers.setdefault('accept', 'text/plain')
        elif body is not None:
            data = body
        else:
            data = ''
        return data, headers

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
             body: Optional[bytes | str] = None,
             headers: Optional[dict] = None):
        if self._session:
            body, headers = self._prepare_data(form, json, body, headers)
            self._session.request(method='POST', url=url, body=body, headers=headers)
            return Response(self._session.getresponse())

    def put(self,
            url: str,
            form: Optional[dict] = None,
            json: Optional[dict] = None,
            body: Optional[bytes | str] = None,
            headers: Optional[dict] = None):
        if self._session:
            body, headers = self._prepare_data(form, json, body, headers)
            self._session.request(method='PUT', url=url, body=body, headers=headers)
            return Response(self._session.getresponse())

    def patch(self,
              url: str,
              form: Optional[dict] = None,
              json: Optional[dict] = None,
              body: Optional[bytes | str] = None,
              headers: Optional[dict] = None):
        if self._session:
            body, headers = self._prepare_data(form, json, body, headers)
            self._session.request(method='PATCH', url=url, body=body, headers=headers)
            return Response(self._session.getresponse())

    def delete(self,
               url: str,
               form: Optional[dict] = None,
               json: Optional[dict] = None,
               headers: Optional[dict] = None):
        if self._session:
            body, headers = self._prepare_data(form, json, headers=headers)
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
        self.headers = {k.lower(): v for k, v in r.getheaders()}
        self.status = r.status
        self.reason = r.reason
        self.message = r.msg
        self.version = r.version
        self.data = r.read()
        if self.headers.get('content-type') == 'application/json':
            self.data = from_json(self.data)
