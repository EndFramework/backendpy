import logging


class Colors:
    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    ORANGE = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'


class Logger(logging.Logger):

    def debug(self, msg, *args, **kwargs):
        super().debug("{}{}{}".format(Colors.BLUE, msg, Colors.ENDC), *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        super().info("{}{}{}".format(Colors.GREEN, msg, Colors.ENDC), *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        super().warning("{}{}{}".format(Colors.ORANGE, msg, Colors.ENDC), *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        super().error("{}{}{}".format(Colors.RED, msg, Colors.ENDC), *args, **kwargs)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        super().exception("{}{}{}".format(Colors.RED, msg, Colors.ENDC), *args, exc_info=exc_info, **kwargs)

    def critical(self, msg, *args, **kwargs):
        super().critical("{}{}{}".format(Colors.RED, msg, Colors.ENDC), *args, **kwargs)


logging.setLoggerClass(Logger)
logging.basicConfig(level=logging.DEBUG)

