Create a project
================

Basic structure
---------------
A Backendpy-based project does not have a mandatory, predetermined structure, and it is the programmer who
decides how to structure his project according to his needs.

The programmer only needs to create a Python module with a custom name (for example "main.py") and set the
instance of :class:`~backendpy.Backendpy` class (which is an ASGI application) inside it.

.. code-block:: python
    :caption: project/main.py

    from backendpy import Backendpy

    bp = Backendpy()

Also for project settings, the ``config.ini`` file must be created in the same path next to the module.
Check out the :doc:`configurations` section for more information.

Applications
------------
Backendpy projects are developed by components called Applications.
It is also possible to connect third-party apps to the project.

To create an application, first create a package containing the ``main.py`` module in the desired path within
the project (or any other path that can be imported).

Then inside the main.py module of an application we need to set an instance of the :class:`~backendpy.app.App` class.
All parts and settings of an application are assigned by the parameters of the App class.

For example, in the "/apps" path inside the project, we create a package called "hello" and main.py file as follows:

.. code-block:: python
    :caption: project/apps/hello/main.py

    from backendpy.app import App
    from .handlers import routes

    app = App(
        routes=[routes])

.. code-block:: python
    :caption: project/apps/hello/handlers.py

    from backendpy.router import Routes
    from backendpy.response import Text

    routes = Routes()

    @routes.get(r'^/hello-world$')
    async def hello_world(request):
        return Text('Hello World!')

As you can see, we have created another optional module called handlers.py and then introduced the routes
defined in it to the App class instance.
The complete list of App class parameters is described in section :doc:`application_structure`.

Only the items that are introduced to the App class are important to the framework, and the internal structuring
of the applications is completely optional.

Our application is now ready and you just need to enable it in the project config.ini file as follows:

.. code-block::
    :caption: project/config.ini

    [apps]
    active =
        project.apps.hello

To run the project, see the :doc:`run` section.

Refer to the :doc:`apps` section to learn how to develop applications.

Command line
------------
The ``backendpy`` command can also be used to create projects and apps.
To do this, first enter the desired path and then use the following commands:

Project creation
````````````````

.. code-block:: console

    $ backendpy create_project --name myproject

To create a project with more complete sample components:

.. code-block:: console

    $ backendpy create_project --name myproject --full

App creation
````````````

.. code-block:: console

    $ backendpy create_app --name myapp

.. code-block:: console

    $ backendpy create_app --name myapp --full

