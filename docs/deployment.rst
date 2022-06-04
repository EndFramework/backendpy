Project deployment
==================
A project based on the Backendpy framework is a standard ASGI application and can use a variety of methods and tools
to deploy and operate these types of applications.

Web servers such as Uvicorn, Hypercorn and Daphne can be used for this purpose.
Also, the features of a web server such as Gunicorn can be used in combination with previous web servers. Or even use
them behind the Nginx web server (as a proxy layer) and take advantage of all the features of this web server.
To use each of these web servers, refer to their documentation.

Example of using Uvicorn:

.. code-block:: console

    uvicorn main:bp --host '127.0.0.1' --port 8000

Example of using Uvicorn with Gunicorn:

.. code-block:: console

    gunicorn main:bp -w 4 -k uvicorn.workers.UvicornWorker

These commands can be defined and managed as a service in the operating system.





