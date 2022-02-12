Installation
============

Requirements
--------------
Python 3.8+

Using pip
--------------
To install the Backendpy framework using pip:

.. code-block:: console

   $ pip3 install backendpy

If you also want to use the optional framework features (such as database, templating, etc.), you can use the following command to install the framework with additional dependencies:

.. code-block:: console

   $ pip3 install backendpy[full]

If you only need one of these features, you can install the required dependencies separately. The list of these requirements is as follows:

.. list-table:: Optional requirements
    :widths: 20 80
    :header-rows: 1

    * - Name
      - Usage
    * - asyncpg
      - If using default ORM
    * - sqlalchemy>=1.4.27
      - If using default ORM
    * - jinja2
      - If using default Templating
    * - aiohttp
      - If using the AsyncHttpClient class of the backendpy.utils.http
    * - requests
      - If using the HttpClient class of the backendpy.utils.http
    * - pillow
      - If using the ModifyImage filter of the backendpy.data_handler.filters
    * - ujson
      - If installed, ujson.loads will be used instead of json.loads, which is faster

You also need to install an ASGI server such as Uvicorn, Hypercorn or Daphne:

.. code-block:: console

   $ pip3 install uvicorn
