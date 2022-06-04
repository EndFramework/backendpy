Applications structure
======================
In section :doc:`project_creation`, we talked about how to create and activate a basic application in
a Backendpy-based project. In this section, we describe the complete components of an application.

As mentioned earlier, a Backendpy-based application does not have a predefined structure or constraint.
In fact, the developer is free to implement the desired architecture for the application and finally import
and configure all the components inside the main module of the application.

The main module of an application must contain an instance of the :class:`~backendpy.app.App` class
that is defined inside a variable called ``app``.
Below is an example of defining an app with all its possible parameters (which are used to assign
components to an application):

.. code-block:: python
    :caption: project/apps/hello/main.py

    from backendpy.app import App
    from .controllers.handlers import routes
    from .controllers.hooks import hooks
    from .controllers.errors import errors
    from .controllers.init import init_func

    app = App(
        routes=[routes],
        hooks=[hooks],
        errors=[errors],
        models=['project.apps.hello.db.models'],
        template_dirs=['templates'],
        init_func=init_func)

An :class:`~backendpy.app.App` class has the following parameters:

.. autoclass:: backendpy.app.App
    :noindex:

In the following, we will describe each of these components of the application, as well as other
items that can be used in applications.
