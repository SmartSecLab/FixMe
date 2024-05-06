import logging
import os
import time
from pathlib import Path


# Configure logger only once
if not hasattr(logging, 'logger_configured'):
    logging.logger_configured = True

    # Create file handler which logs even debug messages
    log_dir = Path('docs/logs')
    log_dir.mkdir(parents=True, exist_ok=True)
    log_filename = log_dir / f'run_{time.strftime("%Y%m%d%H%M%S")}.log'

    # Create a logger
    logger = logging.getLogger('log')
    logger.setLevel(logging.DEBUG)

    # Create file handler which logs even debug messages
    fh = logging.FileHandler(log_filename)
    fh.setLevel(logging.DEBUG)

    # Create formatter and add it to the handler
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(fh)

    # Make the logger accessible globally
    logging.root = logger


def get_logger():
    return logging.root


# # Setup logger
# logger = logger_config.setup_logger()

# # Some sample log messages
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')
