Predefined errors
=================
To return a response with error content, you can manually return the content of that error with :doc:`exceptions`
or create helper classes and assign specific templates to them.
But if the number and variety of these errors is large, it is better to assign a code to each error in addition to
a fixed format for errors.

In the Backendpy framework, a special class for managing error responses is provided to help better and easier manage
errors and their code and to prevent the error code of one application from interfering with other applications:

.. autoclass:: backendpy.error.Error
    :noindex:

In order to use :class:`~backendpy.error.Error` response class, you must first define a list of errors for the
application, including codes and their corresponding messages.
The list of errors in an application is defined by an instance of the :class:`~backendpy.error.ErrorList` class,
which itself contains instances of the :class:`~backendpy.error.ErrorCode` class.

.. autoclass:: backendpy.error.ErrorList
    :noindex:

.. autoclass:: backendpy.error.ErrorCode
    :noindex:

For example, inside a custom module:

.. code-block:: python
    :caption: project/apps/hello/controllers/errors.py

    from backendpy.response import Status
    from backendpy.error import ErrorCode, ErrorList

    errors = ErrorList(
        ErrorCode(1100, "Authorization error", Status.UNAUTHORIZED),
        ErrorCode(1101, "User '{}' does not exists", Status.BAD_REQUEST)
    )

After defining the list of errors, we must add this list to the application. For this purpose, as mentioned before,
inside the ``main.py`` module of the application, we set the ``errors`` parameter with our own error list
(instance of :class:`~backendpy.error.ErrorList` class).

Also note that the errors parameter is a list type, and more than one ErrorList can be assigned to each app,
each list being specific to a different part of the app.

.. code-block:: python
    :caption: project/apps/hello/main.py

    from backendpy.app import App
    from .controllers.errors import errors

    app = App(
        ...
        errors=[errors],
        ...)

And finally, examples of returning the :class:`~backendpy.error.Error` response:

.. code-block:: python
    :caption: project/apps/hello/controllers/handlers.py

    from backendpy.router import Routes
    from backendpy.error import Error

    routes = Routes()

    @routes.get('/example-error')
    async def example_error(request):
        raise Error(1100)

    @routes.post('/login')
    async def login(request):
        raise Error(1101, 'jalil')
