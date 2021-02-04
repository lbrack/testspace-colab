# import os
import datetime
import logging
import logging.config

LOG_PATH = "testspace_colab"
now = datetime.datetime.now()
debug_file_name = now.strftime(f"debug-{LOG_PATH}.log")
logger_config = {
    "version": 1,
    "disable_existing_loggers": False,
    # enables already instantiated loggers (in other modules) to be configured with this approach
    "formatters": {
        "file_formatter": {
            # used in DEBUG log level
            "format": "%(asctime)s.%(msecs)03d - %(name)-15s - %(levelname)-8s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "console_formatter": {
            # used in INFO log level
            "format": "%(name)-15s - %(levelname)-8s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            # INFO messages are being printed to stdout
            "class": "logging.StreamHandler",
            "formatter": "console_formatter",
            "level": "INFO",
            "stream": "ext://sys.stdout",
        },
        "file": {
            # DEBUG messages are being printed to file
            "class": "logging.FileHandler",
            "formatter": "file_formatter",
            "filename": debug_file_name,
            "level": "DEBUG",
        },
    },
    "loggers": {},
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },
}

logging.config.dictConfig(logger_config)
logger = logging.Logger(LOG_PATH)
logger.setLevel(logging.INFO)


def get_logger(name=None):
    """

    :param name:
    :return:
    """
    if name:
        return logger.getChild(name)
    return logger


def set_log_level(level, logger_ref=None):
    """Sets the logging level for the given logger

    :param level: the new log level
    :param logger_ref: If set, only that logger is set, otherwise
           the testspace-colab logger is used
    :return: None
    """
    if not logger_ref:
        logger_ref = get_logger()
    for handler in logging.getLogger().handlers:
        if handler.name == "console":
            handler.setLevel(level)
            logger_ref.setLevel(level)
            break


def remove_log_file():
    """Removes the logfile from the system

    :return:
    """

    logger.debug(
        f"Shutting down logging and removing the {debug_file_name} file "
        f"after a successful run."
    )
    # need to clear all handlers and shut down logging before deleting
    # the debug file:
    logger.root.handlers.clear()
    logging.shutdown()
    # if os.path.isfile(debug_file_name):
    #     try:
    #         os.remove(debug_file_name)
    #     except Exception as os_error:
    #         warnings.warn(f"Failed to erase {debug_file_name} - error {os_error}")
