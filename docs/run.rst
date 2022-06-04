Run
===
You can use different ASGI servers such as Uvicorn, Hypercorn and Daphne to run the project.
For this purpose, you must first install your desired server (see the :doc:`installation` section).

Then enter the project path and use the following commands:

.. code-block:: console
    :caption: For Uvicorn

    $ uvicorn main:bp

.. code-block:: console
    :caption: For Hypercorn

    $ hypercorn main:bp

.. code-block:: console
    :caption: For Daphne

    $ daphne main:bp

.. note::
    In these examples, we assume that the name of the main module of the project is "main.py" and the instance
    name of the Backendpy class inside it is "bp". These names are optional.

The server is now accessible (depending on the host and port running on it) for example at http://127.0.0.1:8000.

For more information on the options of each server, refer to their documentation.
