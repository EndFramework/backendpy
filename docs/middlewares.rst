Middlewares
===========
An ASGI application based on the Backendpy framework (instance of :class:`~backendpy.Backendpy` class) can be used
with a variety of external ASGI middlewares.
In addition to external middlewares, in the Backendpy framework itself, the ability to create middleware for the
internal components and layers of the system is also available.
These types of internal middlewares are discussed below:

Types of middleware
-------------------
The types of Backendpy internal middlewares depending on the layer they are processing are as follows:

Backendpy instance middleware
.............................
This type of middleware, like the external middleware mentioned earlier, processes an ASGI application (instance
of :class:`~backendpy.Backendpy` class) and adds to or modifies its functionality.

The difference between this type of middleware and external middleware is the easier way to create and attach it to
the project, which instead of changing the code, we set it in the project config file.

Request middleware
..................
This middleware takes a :class:`~backendpy.request.Request` object before it reaches the handler layer and delivers a
processed or modified Request object to the handler layer.

Also, depending on the type of processing in this middleware, the middleware can prevent the request process from
continuing and interrupt it with either raise an error response or returning a direct response in the second index
of return tuple and prevent request from reaching the handler layer.

Handler middleware
..................
This middleware takes a request handler (which is an async function) before executing it and returns a processed or
modified handler. As a result, this new handler will be used instead of the original handler to return the response
to this request.

In this middleware, it is also possible to interrupt the process and return the error response.

Response middleware
...................
This middleware captures the final :class:`~backendpy.response.Response` object before sending it to the client and
returns a processed, modified, or replaced Response object.

Creating middleware
-------------------
To create a middleware, use :class:`~backendpy.middleware.middleware.Middleware` class and implement its methods. Each of these
methods is specific to implementing different types of middleware mentioned in the previous section.

How to define these methods is as follows:

.. code-block:: python
    :caption: project/apps/hello/middlewares/example.py

    from backendpy.middleware import Middleware

    class MyMiddleware(Middleware):

        @staticmethod
        def process_application(application):
            ...
            return application

        @staticmethod
        async def process_request(request):
            ...
            return request, None

        @staticmethod
        async def process_handler(request, handler):
            ...
            return handler

        @staticmethod
        async def process_response(request, response):
            ...
            return response

.. autoclass:: backendpy.middleware.middleware.Middleware
    :noindex:

As can be seen, all methods are static and also except for ``process_application`` which is a simple function, all
other methods (which are in the path of handling a request) must be defined as an ``async`` function.

As an example of a request middleware, it can be used to authenticate the user before executing the request handler:

.. code-block:: python
    :caption: project/apps/hello/middlewares/auth.py

    from backendpy.middleware import Middleware
    from backendpy.exception import BadRequest
    ...

    class AuthMiddleware(Middleware):

        @staticmethod
        async def process_request(request):
            auth_token = request.headers.get('authorization')

            if is_invalid_token(auth_token):
                raise BadRequest({'error': 'Invalid auth token'})

            user = get_user(auth_token)

            request.context["auth"] = {
                'user_id': user.id,
                'user_roles': user.roles}

            return request, None

In this example, after receiving a request, first the user identity is checked inside the middleware and if there
is an error, the error response is returned and if successful, the user information is added to the request context
and we can access this information inside the request handler.

Activation of middleware
------------------------
In order to activate a middleware in a project, we need to define them in the project ``config.ini`` file as follows:

.. code-block:: python
    :caption: project/config.ini

    ...
    [middlewares]
    active =
        project.apps.hello.middlewares.auth.AuthMiddleware

The middlewares are independent classes and can be written as part of an application or as a standalone module.
In both cases, to enable them, their class must be added to the project config.
This means that by activating an application, its internal middlewares will not be enabled by default.

.. note::
    Note that in a project you can define an unlimited number of middlewares of one type or in different types.
    Middlewares of the same type will be queued and executed in the order in which they are defined, and the output of
    each middleware will be passed to the next middleware.

