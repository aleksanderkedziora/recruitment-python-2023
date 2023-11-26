import logging
import sys


def setup_loger(name):
    """Helps which getting logger with necessary configuration"""
    logger = logging.getLogger(name)

    running_tests = any("pytest" in arg for arg in sys.argv)

    if not running_tests:
        logger.setLevel(logging.INFO)

        fileHandler = logging.FileHandler(f"logfile.log", mode='a')
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] (%(name)s)  %(message)s')

        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)

    return logger
