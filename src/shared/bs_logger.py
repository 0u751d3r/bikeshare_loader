import logging
import sys

LOGGER_BASE = "bikeshare_loader"
LOGGER_LEVEL = logging.INFO


class BSLogger(object):
    def __init__(self, name: str):
        log_format = '%(asctime)s %(name)s [%(module)s:%(lineno)s](%(levelname)s): %(message)s'
        logger = logging.getLogger(LOGGER_BASE)
        if len(logger.handlers) == 0:
            logger.setLevel(LOGGER_LEVEL)
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(LOGGER_LEVEL)
            handler.setFormatter(logging.Formatter(fmt=log_format, datefmt='%Y-%m-%dT%H:%M:%S'))
            handler.name = LOGGER_BASE
            logger.addHandler(handler)
            logger.debug('Logging setup successful')
        self.logger = logging.getLogger(f"{LOGGER_BASE}.{name}")
        self.logger.setLevel(LOGGER_LEVEL)

    def get_logger(self) -> logging.Logger:
        return self.logger
