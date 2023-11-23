import logging


def setup_loger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    fileHandler = logging.FileHandler(f"logfile.log", mode='a')
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] (%(name)s)  %(message)s')

    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    return logger