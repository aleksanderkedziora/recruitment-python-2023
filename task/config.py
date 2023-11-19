import os

USE_LOCAL = False
DEV = 0

JSON_DATABASE_NAME = "database.json"

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_DATA_SOURCES = os.path.join(ROOT_DIR, 'example_currency_rates.json')
