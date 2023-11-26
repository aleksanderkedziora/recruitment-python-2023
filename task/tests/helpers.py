import os

import decorator
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from task import config
from task.connectors.database.sqlite import SqliteDatabaseConnector, Base


class MockResponse:
    def __init__(self, status_code=200):
        self.status_code = status_code
        self.headers = {'content-type': 'application/json'}

    def json(self):
        return {'rates': [{'mid': 1.0}]}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"HTTP Error {self.status_code}")

    def request_get(self, *args, **kwargs):
        return self


class DbTestConfig:
    DB_URL = f'sqlite:///{config.ROOT_DIR}/task/tests/sqlite3.db'


def with_sqlite_db(func):
    def wrapper(*args, **kwargs):
        original_db_url = SqliteDatabaseConnector.db_url
        SqliteDatabaseConnector.db_url = DbTestConfig.DB_URL

        engine = create_engine(SqliteDatabaseConnector.db_url, echo=True)
        session = Session(engine)

        try:
            Base.metadata.create_all(bind=engine, checkfirst=True)

            args = args[1:]
            func(*args, **kwargs)

        finally:

            session.close()
            try:
                os.remove(SqliteDatabaseConnector.db_url.replace('sqlite:///', ''))
            except FileNotFoundError:
                pass

            SqliteDatabaseConnector.db_url = original_db_url

    return decorator.decorator(wrapper, func)


def with_json_db(func):
    def wrapper(*args, **kwargs):
        original_json_db_path = config.JSON_DATABASE_NAME
        json_file_path = os.path.join(config.ROOT_DIR, 'task/tests/test_database.json')
        config.JSON_DATABASE_NAME = json_file_path
        with open(json_file_path, 'w') as json_file:
            json_file.write('{}')  # Write an empty JSON object

        try:

            args = args[1:]
            func(*args, **kwargs)

        finally:

            os.remove(json_file_path)
        config.JSON_DATABASE_NAME = original_json_db_path
    return decorator.decorator(wrapper, func)


def with_local_source(temporary_json_file_param):
    def outer_wrapper(func):
        def wrapper(*args, **kwargs):

            original_filename = config.LOCAL_DATA_SOURCES
            config.LOCAL_DATA_SOURCES = temporary_json_file_param

            try:
                args = args[1:]
                return func(*args, **kwargs)
            finally:
                config.LOCAL_DATA_SOURCES = original_filename

        return decorator.decorator(wrapper, func)
    return outer_wrapper
