Responses
=========
To respond to a request, we use instances of the :class:`~backendpy.response.Response` class or its subclasses
inside the handler function.
Default Backendpy responses include :class:`~backendpy.response.Text`, :class:`~backendpy.response.HTML`,
:class:`~backendpy.response.JSON`, :class:`~backendpy.response.Binary`, :class:`~backendpy.response.File`,
and :class:`~backendpy.response.Redirect`, but you can also create your own custom response types by extending
the :class:`~backendpy.response.Response` class.

The details of each of the default response classes are as follows:

.. autoclass:: backendpy.response.Response
    :noindex:

.. autoclass:: backendpy.response.Text
    :noindex:

Example usage:

.. code-block:: python
    :caption: project/apps/hello/handlers.py

    from backendpy.router import Routes
    from backendpy.response import Text

    routes = Routes()

    @routes.get('/hello-world')
    async def hello_world(request):
        return Text('Hello World!')


.. autoclass:: backendpy.response.JSON
    :noindex:

Example usage:

.. code-block:: python
    :caption: project/apps/hello/handlers.py

    from backendpy.router import Routes
    from backendpy.response import JSON

    routes = Routes()

    @routes.get('/hello-world')
    async def hello_world(request):
        return JSON({'message': 'Hello World!'})


.. autoclass:: backendpy.response.HTML
    :noindex:

Example usage:

.. code-block:: python
    :caption: project/apps/hello/handlers.py

    from backendpy.router import Routes
    from backendpy.response import HTML

    routes = Routes()

    @routes.get('/hello-world')
    async def hello_world(request):
        return HTML('<html><body>Hello World!</body></html>')


.. autoclass:: backendpy.response.Binary
    :noindex:

.. autoclass:: backendpy.response.File
    :noindex:

Example usage:

.. code-block:: python
    :caption: project/apps/hello/handlers.py

    import os
    from backendpy.router import Routes
    from backendpy.response import File

    routes = Routes()

    @routes.get('/hello-world')
    async def hello_world(request):
        return File(os.path.join('images', 'logo.jpg'))


.. autoclass:: backendpy.response.Redirect
    :noindex:

There is another type of response to quickly return a success response in predefined json format,
which is as follows:

.. autoclass:: backendpy.response.Success
    :noindex:

Example usage:

.. code-block:: python
    :caption: project/apps/hello/handlers.py

    from backendpy.router import Routes
    from backendpy.response import Success

    routes = Routes()

    @routes.get('/hello-world')
    async def hello_world(request):
        return Success()

    @routes.post('/login')
    async def login(request):
        return Success('Successful login!')

.. note::
    The json format used in the :class:`~backendpy.response.Success` response is similar to the
    :class:`~backendpy.error.Error` response, and these two types of responses can be used together in a project.
    Refer to the :doc:`predefined_errors` section for information on how to use the :class:`~backendpy.error.Error`
    response.