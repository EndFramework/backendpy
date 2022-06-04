Exceptions
==========
Backendpy exceptions are the type of responses used to return HTTP errors and can also be raised.

.. note::
   As mentioned, Backendpy exceptions are the type of :class:`~backendpy.response.Response` and their
   content is returned as a response and displayed to the user. Therefore, these exceptions should be used
   only for errors that must be displayed to users, and any kind of internal system error should be created
   with normal Python exceptions, in which case, the :class:`~backendpy.exception.ServerError` response is
   displayed to the user with a public message and does not contain sensitive system information that may
   be contained in the internal exception message.

The list of default exception response classes are as follows:

.. autoclass:: backendpy.exception.ExceptionResponse
    :noindex:

.. autoclass:: backendpy.exception.BadRequest
    :noindex:

Example usage:

.. code-block:: python
    :caption: project/apps/hello/handlers.py

    from backendpy.router import Routes
    from backendpy.exception import BadRequest

    routes = Routes()

    @routes.post(r'^/login$')
    async def login(request):
        raise BadRequest({'message': 'Login failed!'})

.. autoclass:: backendpy.exception.Unauthorized
    :noindex:

.. autoclass:: backendpy.exception.Forbidden
    :noindex:

.. autoclass:: backendpy.exception.NotFound
    :noindex:

.. autoclass:: backendpy.exception.ServerError
    :noindex:
