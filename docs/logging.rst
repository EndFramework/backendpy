Logging
=======
The Backendpy framework provides a logging class that uses Python standard logging module and differs in the color
display of the logs in the command line, which increases the readability of the logs in this environment.

This module has ``get_logger()`` function with the following specifications:

.. autofunction:: backendpy.logging::get_logger
    :noindex:

Example:

.. code-block:: python

    from backendpy import logging

    LOGGER = logging.get_logger(__name__)

    LOGGER.debug("Example debug log")
    LOGGER.error("Example error log")
