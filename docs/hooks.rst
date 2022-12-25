Hooks
=====
Sometimes it is necessary to perform a specific operation following an event. For these types of needs, we can use
Backendpy hooks feature.
For example, when we want to write an email management application that sends an email after certain events in other
applications, such as the registration or login of users.

With this feature, we can both define new events with special labels within our application as points so that others
can write their own code for these events to run, or we can assign codes to execute when triggering other events on
the system.

Event Definition
----------------
To define event points, we use the ``execute_event`` method of the :class:`~backendpy.Backendpy` class instance
inside any space we have access to this instance. (For example, inside the handler of a request, we access the
project :class:`~backendpy.Backendpy` instance via ``request.app``).

Example of defining user creation event:

.. code-block:: python

    @routes.post('/users', data_handler=UserCreationData)
    async def user_creation(request):
        ...
        await request.app.execute_event('user_created')
        ...

If the event also contains arguments, we send them in the second parameter in the form of a dictionary:

.. code-block:: python

    @routes.post('/users', data_handler=UserCreationData)
    async def user_creation(request):
        ...
        await request.app.execute_event('user_created', {'username': username})
        ...


Default Events
..............
In addition to the events that developers can add to the project, the default events are also provided in the
framework as follows:

.. list-table:: Framework Default Events
    :widths: 30 70
    :header-rows: 1

    * - Label
      - Description
    * - ``startup``
      - After successfully starting the ASGI server
    * - ``shutdown``
      - After the ASGI server shuts down
    * - ``request_start``
      - At the start of a request
    * - ``request_end``
      - After the response to a request is returned


Hook Definition
---------------
To define the code that is executed in events, we use the :class:`~backendpy.hook.Hooks` class and its ``event``
decorator:

.. code-block:: python
    :caption: project/apps/hello/controllers/hooks.py

    from backendpy.hook import Hooks
    from backendpy.logging import get_logger

    LOGGER = get_logger(__name__)
    hooks = Hooks()

    @hooks.event('startup')
    async def example():
        LOGGER.debug("Server starting")

    @hooks.event('user_created')
    async def example2(username):
        LOGGER.debug(f"User '{username}' creation")

As can be seen, if an argument is sent to a hook, these arguments are received in the parameters of the hook functions,
otherwise they have no parameter.

Here we have written the hooks inside a custom module. To connect these hooks to the application, like the other
components, we use the ``main.py`` module of the application:

.. code-block:: python
    :caption: project/apps/hello/main.py

    from backendpy.app import App
    from .controllers.hooks import hooks

    app = App(
        ...
        hooks=[hooks],
        ...)

Another way to use hooks is to attach them directly to a project (instead of an application), which can be used for
special purposes such as managing database connections, which are part of the project-level settings:

.. code-block:: python
    :caption: project/main.py

    from backendpy import Backendpy

    bp = Backendpy()

    @bp.event('startup')
    async def on_startup():
        LOGGER.debug("Server starting")
