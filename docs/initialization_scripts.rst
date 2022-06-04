Initialization scripts
======================
Some applications require basic data in order to run. For example, the users application, after installation, also
needs to enter the administrator account information to be able to manage other accounts and the entire system.
To record this raw data, we can use initialization scripts that are executable at the command line when a project is
deployed.

From the ``init_func`` parameter of any application we can assign an initialization function to it:

.. code-block:: python
    :caption: project/apps/hello/main.py

    from backendpy.app import App
    from .controllers.init import init_data

    app = App(
        ...
        init_func=init_data,
        ...)

And an init function could be like this:

.. code-block:: python
    :caption: project/apps/hello/controllers/init.py

    from asyncio import current_task
    from backendpy.db import get_db_engine, get_db_session
    from backendpy.logging import logging
    from ..db import queries

    LOGGER = logging.getLogger(__name__)

    async def init_data(config):
        # Get db session
        db_engine = get_db_engine(config['database'], echo=False)
        db_session = get_db_session(db_engine, current_task)

        try:
            # ...
            # Create admin user
            if await queries.get_users(db_session):
                LOGGER.warning('Users created already [SKIPPED]')
            else:
                try:
                    user_data = {
                        'first_name': input('Enter first name:\n'),
                        'last_name': input('Enter last name:\n'),
                        'username': input('Enter admin username:\n'),
                        'password': input('Enter admin password:\n')}
                except Exception as e:
                    raise Exception(f'Input error:\n{e}')

                if await queries.set_user(db_session, user_data):
                    LOGGER.info('Admin user created successfully')
                else:
                    raise Exception('Admin user creation error')
        finally:
            await db_session.remove()
            await db_engine.dispose()

As can be seen, the init functions receive ``config`` parameter, which can be used to access project configurations
such as database information and so on.

The project manager can perform the initialization by executing the following command on the command line in the
project dir:

.. code-block:: console

    $ backendpy init_project

By executing this command, the Backendpy framework executes the initialization scripts of all applications activated
in the project configuration sequentially.
