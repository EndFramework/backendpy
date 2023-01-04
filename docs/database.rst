Database
========
In Backendpy, developers can use any database system of their choice, depending on the needs of the project, using any
type of engine layer that supports async requests, so there is no mandatory structure for this.
However, this framework will provide helpers to speed up work with various database systems. Helpers are currently
available for Sqlalchemy.

Use custom database
-------------------
With the :doc:`hooks` feature described in the previous sections, you can easily configure your connections, sessions,
and database system according to different system events.

For example:

.. code-block:: python
    :caption: project/main.py

    from backendpy import Backendpy
    ...

    bp = Backendpy()

    @bp.event('startup')
    async def on_startup():
        bp.context['db_engine'] = get_db_engine(config=bp.config['database'])
        bp.context['db_session'] = get_db_session(engine=bp.context['db_engine'], scope_func=bp.get_current_request)

    @bp.event('shutdown')
    async def on_shutdown():
        await bp.context['db_engine'].dispose()

    @bp.event('request_end')
    async def on_request_end():
        await bp.context['db_session'].remove()

And then we use these resources inside the project:

.. code-block:: python

    @routes.get('/hello-world')
    async def hello(request):
        db_session = request.app.context['db_session']()
        ...

In this example, we used the ``startup`` event to initialize the engine and connect to the database at the start of
the service, the ``request_end`` event to remove the dedicated database session of each request at the end of it, and
the ``shutdown`` event to close the database connection when the service shuts down.

Depending on your architecture for managing database connections and sessions, you may want to make the scope of each
database session dependent on anything like threads and so on.
In this example, the database sessions are set based on the scope of each request, which means that when a request
starts, a database session starts (if requested inside the handler by calling db_session) and closes at the end of the
request.
The Backendpy framework provides the ``get_current_request`` as a callable for specifying session scope, which can be
set in your engine or ORM settings.

Note that in the example above, the names of some functions such as get_db_engine, etc. are used, which have only the
aspect of an example and must be implemented by the developer according to the database system used.
For more information, you can refer to the specific engine, database or ORM guides you use.

Use Sqlalchemy helper layer
---------------------------
When using Sqlalchemy ORM, Backendpy provides default helpers for this package, which makes it easier to work with.

.. note::
    Async capability has been added from Sqlalchemy version 1.4.27, so lower versions are not compatible with
    Backendpy framework.
    Also, among the available engines, only those that support async are usable, such as ``asyncpg`` package, which
    can be used based on the ``Postgresql`` database system.

To use Sqlalchemy in Backendpy projects, do the following:

First, in order to set the database engine and session settings into the project, we use the helper function
``set_database_hooks()`` as follows:

.. code-block:: python
    :caption: project/main.py

    from backendpy import Backendpy
    from backendpy.db import set_database_hooks

    bp = Backendpy()
    set_database_hooks(bp)

In addition to setting up the engine and creating and deleting the database connection at the start and shutdown of
the service, this function also sets database sessions for the scope of each request, which can be used by calling
``request.app.context['db_session']`` inside the request handler:

.. code-block:: python

    @routes.get('/hello-world')
    async def hello(request):
        db_session = request.app.context['db_session']()
        ...

The database settings should also be stored in the config.ini file as follows, and the framework will use these
settings to connect to the database:

.. code-block::
    :caption: project/config.ini

    [database]
    host = localhost
    port = 5432
    name = your_db_name
    username = your_db_user
    password = your_db_password

After setting up the project, here's how to use Sqlalchemy ORM in applications:

To create models of an application, inside the desired module of the application, we use the :class:`~backendpy.db.Base`
class as follows:

.. code-block:: python
    :caption: project/apps/hello/db/models.py

    from sqlalchemy import Column, Integer, String
    from backendpy.db import Base

    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer(), primary_key=True)
        first_name = Column(String(50))
        last_name = Column(String(50))

If you use this Base class, it is possible to connect between models of different applications, and also the CLI
commands of the framework related to the database can be used.

After defining the data models, these models should also be introduced to the application (so that they can be imported
when needed for the framework). For this purpose, according to the procedure of other sections, we will use ``main.py``
module of the application:

.. code-block:: python
    :caption: project/apps/hello/main.py

    from backendpy.app import App

    app = App(
        ...
        models=['project.apps.hello.db.models'],
        ...)

As shown in the example, to introduce the models, we set their module path as a string to the application ``models``
parameter. This parameter is of iterable type and several model modules can be assigned to it.
These module paths must also be within valid Python path. In this example, it is inside the project path that has
already been added to the Python path by default.

We can now use database queries in any part of the application:

.. code-block:: python
    :caption: project/apps/hello/db/queries.py

    from .models import User

    async def get_user(session, identifier):
        return await session.get(User, identifier)

.. code-block:: python
    :caption: project/apps/hello/controllers/handlers.py

    ...
    from ..db import queries

    @routes.get('/users/<id:int>', data_handler=UserFilterData)
    async def user_detail(request):
        data = await request.get_cleaned_data()
        db_session = request.app.context['db_session']()
        result = await queries.get_user(db_session, data['id'])
        return Success(to_dict(result))

Note that in the sample code above, some functions such as to_dict or UserFilterData, etc. are used, which have an
example aspect and must be created by the developer.

For more information about Sqlalchemy and how to use it, you can refer to its specific documentation.

Create database and models with command line
............................................
If you use the default Sqlalchemy layer as described above, you can automatically create the database and all data
models within the project after entering the project path in the command line and using the following command:

.. code-block:: console

   $ backendpy create_db

