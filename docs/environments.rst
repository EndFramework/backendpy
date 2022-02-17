Environments
============

In Backendpy framework, it is possible to use different environments for project execution (such as development,
production, etc.).

Each environment has a different config file and can have different database settings, media paths, and so on.

In a development team, different parts of the team can use their own environments and settings to execute and work
on the project.
Also, if needed on the main server, the project can be executed with another configuration in parallel, on another
host or port.

To do this, you need to define the ``BACKENDPY_ENV`` variable in the os with the desired name for the environment.
For example, to define an environment called "dev", we use the following command:

.. code-block:: console

    $ export BACKENDPY_ENV=dev

You must also create and configure a separate configuration file named ``config.dev.ini``.

Now if the server runs (in the process that the environmental variable is exported) or when other backendpy
management commands are executed, this configuration will be used instead of the original configuration.
