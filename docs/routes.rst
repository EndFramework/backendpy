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
To define :class:`~backendpy.router.Route` we can use :func:`~backendpy.router.Routes.get`,
:func:`~backendpy.router.Routes.post`, :func:`~backendpy.router.Routes.path`,
:func:`~backendpy.router.Routes.put` and :func:`~backendpy.router.Routes.delete` decorators
as follows:

.. code-block:: python
    :caption: project/apps/hello/handlers.py

    from backendpy.router import Routes
    from backendpy.response import Text

    routes = Routes()

    @routes.get('/hello-world')
    async def hello_world(request):
        return Text('Hello World!')

    @routes.post('/login')
    async def login(request):
        ...

Also, if we need to access a handler with different http methods, we can use
:func:`~backendpy.router.Routes.route` decorator as follows:

.. code-block:: python
    :caption: project/apps/hello/handlers.py

    from backendpy.router import Routes
    from backendpy.response import Text

    routes = Routes()

    @routes.route('/hello-world', ('GET', 'POST'))
    async def hello_world(request):
        return Text('Hello World!')

Separate routes
---------------
We can define the list of :class:`~backendpy.router.Route` separately from the handlers as follows:

.. code-block:: python
    :caption: project/apps/hello/handlers.py

    from backendpy.response import Text

    async def hello_world(request):
        return Text('Hello World!')

    async def login(request):
        ...

.. code-block:: python
    :caption: project/apps/hello/urls.py

    from backendpy.router import Routes, Route
    from .handlers import hello_world, login

    routes = Routes(
        Route('/hello-world', ('GET',), hello_world),
        Route('/login', ('POST',), login)
    )

As can be seen in the examples, in both cases, the :class:`~backendpy.router.Routes` object
is defined, which is used to hold the list of :class:`~backendpy.router.Route`.

The complete list of parameters of a :class:`~backendpy.router.Route` is as follows:

.. autoclass:: backendpy.router.Route
    :noindex:

Note that in ``@route`` decorator, which is defined on the handler function itself, the ``handler``
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
can be used to define the routes of separate parts of the application or even different
versions of the API and the like. For example:

.. code-block:: python
    :caption: project/apps/hello/main.py

    from backendpy.app import App
    from .handlers.v1 import routes as routes_v1
    from .handlers.v2 import routes as routes_v2

    app = App(
        routes=[routes_v1, routes_v2])

Url variables
-------------
In order to get variable values from URL, they can be specified by ``<`` and ``>`` characters inside the route.

.. code-block:: python
    :caption: project/apps/hello/handlers.py

    from backendpy.router import Routes

    routes = Routes()

    @routes.patch('/users/<id>')
    async def user_modification(request):
        id = request.url_vars['id']
        ...

The default matchable data type of variables is string.
You can also specify the type of value that can be matched in the URL with the ``:`` separator.

.. code-block:: python
    :caption: project/apps/hello/handlers.py

    from backendpy.router import Routes

    routes = Routes()

    @routes.patch('/users/<id:int>')
    async def user_modification(request):
        id = int(request.url_vars['id'])
        ...

Allowed data types are ``str``, ``int``, ``float`` and ``uuid``.

.. note::
    Note that these data types determine the matchable data type in the URL,
    and not the data converter to related types in Python, and these data
    will be available with the Python string data type.
    In order to automatically convert types of received data, as well as
    to access various features of working with input data, refer to the
    :doc:`data_handlers` section.

Priority
--------
Pay attention that when defining the routes, if several routes overlap, the route
that is defined in a non-variable and explicit way will be matched first. If the
routes are the same in this respect, they will be prioritized according to the order
of their definition in the code.
For example, ``/users/posts`` and ``/users/1`` will take precedence over ``/users/<id>``,
even if they are defined in the code after that.
