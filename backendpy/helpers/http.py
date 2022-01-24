try:
    import aiohttp
except ImportError:
    pass

try:
    import requests
except ImportError:
    pass


class AsyncHttpClient:

    def __init__(self):
        self.session = None
        self._session = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    async def get(self, url, headers=None):
        if self._session:
            async with self._session.get(url, headers=headers) as response:
                return await response.json() \
                    if response.content_type == 'application/json' else await response.text()

        elif self.session:
            async with self.session.get(url, headers=headers) as response:
                return await response.json() \
                    if response.content_type == 'application/json' else await response.text()

    async def post(self, url, data=None, json=None, headers=None):
        if self._session:
            async with self._session.post(url, data=data, json=json, headers=headers) as response:
                return await response.json() \
                    if response.content_type == 'application/json' else await response.text()

        elif self.session:
            async with self.session.post(url, data=data, json=json, headers=headers) as response:
                return await response.json() \
                    if response.content_type == 'application/json' else await response.text()

    async def put(self, url, data=None, json=None, headers=None):
        if self._session:
            async with self._session.put(url, data=data, json=json, headers=headers) as response:
                return await response.json() \
                    if response.content_type == 'application/json' else await response.text()

        elif self.session:
            async with self.session.put(url, data=data, json=json, headers=headers) as response:
                return await response.json() \
                    if response.content_type == 'application/json' else await response.text()

    async def patch(self, url, data=None, json=None, headers=None):
        if self._session:
            async with self._session.patch(url, data=data, json=json, headers=headers) as response:
                return await response.json() \
                    if response.content_type == 'application/json' else await response.text()

        elif self.session:
            async with self.session.patch(url, data=data, json=json, headers=headers) as response:
                return await response.json() \
                    if response.content_type == 'application/json' else await response.text()

    async def delete(self, url, data=None, json=None, headers=None):
        if self._session:
            async with self._session.delete(url, data=data, json=json, headers=headers) as response:
                return await response.json() \
                    if response.content_type == 'application/json' else await response.text()

        elif self.session:
            async with self.session.delete(url, data=data, json=json, headers=headers) as response:
                return await response.json() \
                    if response.content_type == 'application/json' else await response.text()

    async def start_session(self):
        self.session = aiohttp.ClientSession()

    async def close_session(self):
        if self.session:
            await self.session.close()


class HttpClient:

    def __init__(self):
        self.session = None
        self._session = None

    def __enter__(self):
        self._session = requests.session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            self._session.close()

    def get(self, url, headers=None):
        if self._session:
            result = self._session.get(url, headers=headers)
            return result.json if result.json else result.text
        elif self.session:
            result = self.session.get(url, headers=headers)
            return result.json if result.json else result.text

    def post(self, url, data=None, json=None, headers=None):
        if self._session:
            result = self._session.post(url, data=data, json=json, headers=headers)
            return result.json if result.json else result.text

        elif self.session:
            result = self.session.post(url, data=data, json=json, headers=headers)
            return result.json if result.json else result.text

    def put(self, url, data=None, json=None, headers=None):
        if self._session:
            result = self._session.put(url, data=data, json=json, headers=headers)
            return result.json if result.json else result.text

        elif self.session:
            result = self.session.put(url, data=data, json=json, headers=headers)
            return result.json if result.json else result.text

    def patch(self, url, data=None, json=None, headers=None):
        if self._session:
            result = self._session.patch(url, data=data, json=json, headers=headers)
            return result.json if result.json else result.text

        elif self.session:
            result = self.session.patch(url, data=data, json=json, headers=headers)
            return result.json if result.json else result.text

    def delete(self, url, data=None, json=None, headers=None):
        if self._session:
            result = self._session.delete(url, data=data, json=json, headers=headers)
            return result.json if result.json else result.text

        elif self.session:
            result = self.session.delete(url, data=data, json=json, headers=headers)
            return result.json if result.json else result.text

    async def start_session(self):
        self.session = requests.session()

    def close_session(self):
        if self.session:
            self.session.close()
