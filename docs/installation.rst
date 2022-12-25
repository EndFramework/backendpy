Installation
============

Requirements
------------
Python 3.8+

Using pip
---------
To install the Backendpy framework using pip:

.. code-block:: console

   $ pip3 install backendpy

If you also want to use the optional framework features (such as database, templating, etc.), you can use the
following command to install the framework with additional dependencies:

.. code-block:: console

   $ pip3 install backendpy[full]

If you only need one of these features, you can install the required dependencies separately. The list of these
requirements is as follows:

.. list-table:: Optional requirements
    :widths: 15 15 70
    :header-rows: 1

    * - Name
      - Version
      - Usage
    * - asyncpg
      - >=0.25.0
      - If using default ORM
    * - sqlalchemy
      - >=1.4.27
      - If using default ORM
    * - jinja2
      - >=3.0.0
      - If using default Templating
    * - pillow
      - >=9.0.0
      - If using the ModifyImage filter of the backendpy.data_handler.filters
    * - ujson
      - >=5.1.0
      - If installed, ujson.loads will be used instead of json.loads, which is faster

You also need to install an ASGI server such as Uvicorn, Hypercorn or Daphne:

.. code-block:: console

   $ pip3 install uvicorn
