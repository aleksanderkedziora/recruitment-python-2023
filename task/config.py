import os


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_DATA_SOURCES = os.path.join(ROOT_DIR, 'example_currency_rates.json')
JSON_DATABASE_NAME = os.path.join(ROOT_DIR, 'database.json')
ISO_CODE_BASE = os.path.join(ROOT_DIR, 'currency_iso_codes.json')

RUN_CONFIG = {
    'MODE': '',
    'SOURCE': ''
}
