Routes
======
Routes in an application are the accessible URLs defined for that application.
The routes of an application are defined according to a specific format, and for each
route, a handler function is assigned. When each request reaches the server, if the request
url matches with a route, the request will be delivered to the handler of that route.

Generally, there are two ways to define routes, one is to use Python decorators on top of
handler functions, and the other is to use a separate section like urls.py file containing
a list of all the routes and linking them to the handlers. For different developers and
depending on the architecture of the application, each of these methods can take precedence
over the other.
One of the features of the Backendpy framework is the possibility of defining routes in both methods.

Consider the following examples:

Decorator based routes
----------------------
To define :class:`~backendpy.router.Uri` we can use :func:`~backendpy.router.Routes.get`,
:func:`~backendpy.router.Routes.post`, :func:`~backendpy.router.Routes.path`,
:func:`~backendpy.router.Routes.put` and :func:`~backendpy.router.Routes.delete` decorators
as follows:

.. code-block:: python
    :caption: project/apps/hello/handlers.py

    from backendpy.router import Routes
    from backendpy.response import Text

    routes = Routes()

    @routes.get(r'^/hello-world$')
    async def hello_world(request):
        return Text('Hello World!')

    @routes.post(r'^/login$')
    async def login(request):
        ...

Also, if we need to access a handler with different http methods, we can use
:func:`~backendpy.router.Routes.uri` decorator as follows:

.. code-block:: python
    :caption: project/apps/hello/handlers.py

    from backendpy.router import Routes
    from backendpy.response import Text

    routes = Routes()

    @routes.uri(r'^/hello-world$', ('GET', 'POST'))
    async def hello_world(request):
        return Text('Hello World!')

Separate routes
---------------
We can define the list of :class:`~backendpy.router.Uri` separately from the handlers as follows:

.. code-block:: python
    :caption: project/apps/hello/handlers.py

    from backendpy.response import Text

    async def hello_world(request):
        return Text('Hello World!')

    async def login(request):
        ...

.. code-block:: python
    :caption: project/apps/hello/urls.py

    from backendpy.router import Routes, Uri
    from .handlers import hello_world, login

    routes = Routes(
        Uri(r'^/hello-world$', ['GET'], hello_world),
        Uri(r'^/login', ['POST'], login),
    )

As can be seen in the examples, in both cases, the :class:`~backendpy.router.Routes` object
is defined, which is used to hold the list of :class:`~backendpy.router.Uri`.

The complete list of parameters of a :class:`~backendpy.router.Uri` is as follows:

.. autoclass:: backendpy.router.Uri
    :noindex:

Note that in ``@uri`` decorator, which is defined on the handler function itself, the ``handler``
parameter does not exist. and in ``@get``,``@post`` and ... decorators, the ``method``
parameter also does not exist.

After defining the routes, the Routes object can then be assigned to the application via
the :class:`~backendpy.app.App` class ``routes``parameter in the ``main.py`` module of
the application:

.. code-block:: python
    :caption: project/apps/hello/main.py

    from backendpy.app import App
    from .handlers import routes

    app = App(
        routes=[routes])

In an application, more than one object of the Routes class can be defined. Each of which
can be used to define the Uri of separate parts of the application or even different
versions of the API and the like. For example:

.. code-block:: python
    :caption: project/apps/hello/main.py

    from backendpy.app import App
    from .handlers.v1 import routes as routes_v1
    from .handlers.v2 import routes as routes_v2

    app = App(
        routes=[routes_v1, routes_v2])
