from logging.handlers import RotatingFileHandler
import logging

from brokers.settings import log_direction


def config_logging(log_level, filename, logger_name):
    logger = logging.getLogger(logger_name)
    if not logger.handlers:
        logger.setLevel(log_level)
        log_formatter = logging.Formatter(fmt='%(asctime)s__%(name)s__%(levelname)s :  %(message)s')
        # file_logger = logging.FileHandler(filename="logs/" + filename)
        file_logger = RotatingFileHandler(filename=log_direction + filename, maxBytes=1*1024*1024, backupCount=5)
        file_logger.setFormatter(log_formatter)
        logger.addHandler(file_logger)

    return logger


def set_logging():
    # general_logger = logging.getLogger()
    logging.getLogger().setLevel(logging.ERROR)
    log_formatter = logging.Formatter(fmt='%(asctime)s__%(name)s__%(levelname)s :  %(message)s')
    # if not general_logger.handlers:
    general_file_logger = RotatingFileHandler(filename=log_direction + "error.log", maxBytes=1 * 1024 * 1024, backupCount=5)
    general_file_logger.setFormatter(log_formatter)
    logging.getLogger().addHandler(general_file_logger)