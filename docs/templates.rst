Templates
=========
The need to render templates on the server side is used in some projects. External template engines that support async
can be used for this purpose. You can also use the framework helper layer for this, which is a layer for using the
Jinja2 template engine package.
The Backendpy framework facilitates the use of templates with this template engine and adapts it to its architecture
with things like template files async reading from predefined application template paths.

An example of rendering a web page template and returning it as a response is as follows.

First we need to specify the application template dirs inside the application ``main.py`` module with the
``template_dirs`` parameter of the App class:

.. code-block:: python
    :caption: project/apps/hello/main.py

    from backendpy.app import App

    app = App(
        ...
        template_dirs=['templates'],
        ...)

Then we create the desired templates in the defined path:

.. code-block:: html
    :caption: project/apps/hello/templates/home.html

    <!DOCTYPE html>
    <html>
    <head>
        <title>Backendpy</title>
    </head>
    <body>
      <h1>{{ message }}</h1>
    </body>
    </html>

Refer to the Jinja2 package documentation to learn the templates syntax.

Finally, we use these template inside a handler:

.. code-block:: python
    :caption: project/apps/hello/controllers/handlers.py

    from backendpy.router import Routes
    from backendpy.response import HTML
    from backendpy.templating import Template

    routes = Routes()

    @routes.get('/home')
    async def home(request):
        context = {'message': 'Hello World!'}
        return HTML(await Template('home.html').render(context))

In this example code, we first initialize :class:`~backendpy.templating.Template` class with the template name and
then with the ``render`` method we render the context values in it (note that this method must also be called async)
and then we return the final content with :class:`~backendpy.response.HTML` response.

Also here you just need to enter the template name and the framework will automatically search for this name in the
application template dirs.

Details of the :class:`~backendpy.templating.Template` class are as follows:

.. autoclass:: backendpy.templating.Template
    :noindex:
