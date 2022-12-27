from ..middleware import Middleware
from ...response import Status, Response


class CORSMiddleware(Middleware):

    @staticmethod
    async def process_request(request):
        if request.method == 'OPTIONS':
            config = request.app.config.get('cors', {})
            response_headers = dict()

            if 'origin' in request.headers:
                requested_origin = request.headers.get('origin')
                if requested_origin:
                    allowed_origins = config.get('allowed_origins')
                    if allowed_origins:
                        if allowed_origins != '*' and type(allowed_origins) is str:
                            allowed_origins = [allowed_origins]
                        if allowed_origins == '*' or requested_origin.lower() in allowed_origins:
                            response_headers['access-control-allow-origin'] = requested_origin

                            requested_method = request.headers.get('access-control-request-method')
                            if requested_method:
                                allowed_methods = config.get('allowed_methods')
                                if allowed_methods:
                                    if allowed_methods == '*':
                                        allowed_methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE', 'OPTIONS', 'HEAD']
                                    elif type(allowed_methods) is str:
                                        allowed_methods = [allowed_methods.upper()]
                                    else:
                                        allowed_methods = list(map(str.upper, allowed_methods))
                                    if requested_method.upper() in allowed_methods:
                                        response_headers['access-control-allow-methods'] = ', '.join(allowed_methods)

                            requested_headers = \
                                list(map(str.lower, request.headers.get('access-control-request-headers')
                                         .replace(' ', '').split(',')))
                            if requested_headers:
                                allowed_headers = config.get('allowed_headers')
                                if allowed_headers:
                                    if allowed_headers != '*':
                                        if type(allowed_headers) is str:
                                            allowed_headers = [allowed_headers.lower()]
                                        else:
                                            allowed_headers = list(map(str.lower, allowed_headers))
                                    allowed_requested_headers = requested_headers if allowed_headers == '*' else \
                                        (h for h in requested_headers if h in allowed_headers)
                                    response_headers['access-control-allow-headers'] = \
                                        ', '.join(allowed_requested_headers)

                                    if config.get('allow_credentials') == 'true' \
                                            and ('authorization' in allowed_requested_headers
                                                 or 'proxy-authorization' in allowed_requested_headers
                                                 or 'cookie' in allowed_requested_headers
                                                 or 'client-cert' in allowed_requested_headers
                                                 or 'client-cert-chain' in allowed_requested_headers):
                                        response_headers['access-control-allow-credentials'] = 'true'

                            if response_headers:
                                response_headers['access-control-max-age'] = config.get('max-age', '86400')

            response_headers['vary'] = 'origin'

            response = Response(
                status=Status.NO_CONTENT,
                body=b'',
                headers=list(response_headers.items()))

            return request, response
        else:
            return request, None

    @staticmethod
    async def process_response(request, response):
        if request.method != 'OPTIONS':
            response_headers = dict(response.headers) if response.headers is not None else dict()
            if 'origin' in request.headers:
                requested_origin = request.headers.get('origin')
                if requested_origin:
                    config = request.app.config.get('cors', {})
                    allowed_origins = config.get('allowed_origins')
                    if allowed_origins:
                        if allowed_origins != '*' and type(allowed_origins) is str:
                            allowed_origins = [allowed_origins]
                        if allowed_origins == '*' or requested_origin.lower() in allowed_origins:
                            response_headers['access-control-allow-origin'] = requested_origin
                            if config.get('allow_credentials') == 'true' \
                                and ('authorization' in request.headers
                                     or 'proxy-authorization' in request.headers
                                     or 'cookie' in request.headers
                                     or 'client-cert' in request.headers
                                     or 'client-cert-chain' in request.headers):
                                response_headers['access-control-allow-credentials'] = 'true'
            vary = response_headers.get('vary')
            response_headers['vary'] = ', '.join(set(vary.replace(' ', '').split(',') + ['origin'])) \
                if vary else 'origin'
            response.headers = list(response_headers.items())
        return response
