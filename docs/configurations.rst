Configurations
==============
In Backendpy projects, all the settings of a project are defined in the ``config.ini`` file, which is located in the
root path of each project and next to the main module of the project.
This config file is defined in INI format, which includes sections and options.
The basic list of framework configs and example of their definition is as follows:

.. code-block::
    :caption: project/config.ini

    ; Backendpy Configurations

    [networking]
    stream_size = 32768

    [environment]
    media_path = /foo/bar

    [apps]
    active =
        backendpy_accounts
        myproject.apps.myapp

    [middlewares]
    active =
        backendpy_accounts.middleware.auth.AuthMiddleware

    [database]
    host = localhost
    port = 5432
    name =
    username =
    password =

In ini format, ``;`` is used for comments, ``[]`` is used to define sections, ``key = value`` is used to define values
and the lines are used for list values.

* **networking** section contains values related to the server and the network.

* **environment** section contains values such as the path to the media files and etc.

* **apps** section contains a list of the project active applications.

* **middlewares** section contains a list of the project active middlewares.

* **database** section, if using the default ORM, will include the settings related to it.

Also other custom settings may be required by any of the active apps, which must also be specified in this file.
For example, an account application might have settings like this:

.. code-block::

    [keys]
    aes_key = 11111111111111111111111111111111
    auth_tokens_secret = 2222222222222222222222222222

.. note::

    To protect sensitive information in the config file, such as passwords, private keys, etc., be sure to restrict
    access to this file. For example, set the permission to 600.
