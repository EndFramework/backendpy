Requests
========
HTTP requests, after being received by the framework, become a :class:`~backendpy.request.Request`
object and are sent to the handler functions as a parameter called ``request``.

.. code-block:: python
    :caption: project/apps/hello/handlers.py

    async def hello_world(request):
        ...

Request object contains the following fields:

.. autoclass:: backendpy.request.Request
    :noindex:

