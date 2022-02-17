Management
==========

The following commands can be used by the system administrator:

Creating Database
-----------------
If you are using the default ORM, you can create the database and all data model tables within the project
automatically by the following command (after entering the project path in the command line):

.. code-block:: console

    $ backendpy create_db


Initialization
--------------
Some applications require the initial storage of data in the database, the creation of files, and so on,
before they can be used. For example, before using some systems, information such as user roles, admin
account, etc. related to the users application must be stored in the database.

By running the following command in the project path, Backendpy framework will execute the initialization scripts of
all the apps enabled on the project and will also take the required input data on the command line:

.. code-block:: console

    $ backendpy init_project

