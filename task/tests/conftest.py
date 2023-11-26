import datetime
import json
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from task import config

from task.tests.helpers import MockResponse
from task.utils import Mode, Source


@pytest.fixture
def clean_config():
    config.RUN_CONFIG['MODE'] = ''
    config.RUN_CONFIG['SOURCE'] = ''
    yield


@pytest.fixture
def set_basic_config(clean_config):
    config.RUN_CONFIG['MODE'] = Mode.PROD.value
    config.RUN_CONFIG['SOURCE'] = Source.API.value
    yield


@pytest.fixture
def prod_mode(set_basic_config):
    yield


@pytest.fixture
def dev_mode(set_basic_config):
    config.RUN_CONFIG['MODE'] = Mode.DEV.value
    yield


@pytest.fixture
def api_source(set_basic_config):
    yield


@pytest.fixture
def local_source(set_basic_config):
    config.RUN_CONFIG['SOURCE'] = Source.LOCAL.value
    yield


@pytest.fixture
def temporary_json_file():
    today = datetime.date.today().strftime("%Y-%m-%d")
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        json_data = {
            "EUR": [
                {f"date": f"{today}", "rate": 4.15},
            ],
            "CZK": [
            ]
        }
        json.dump(json_data, temp_file)
        temp_file.flush()

        yield temp_file.name

    temp_file.close()


@pytest.fixture
def mock_nbp_api(monkeypatch):
    mock_response = MockResponse(status_code=200)
    monkeypatch.setattr('task.exchange_rate.requests.get', mock_response.request_get)
    yield


@pytest.fixture(scope='session')
def db_engine(request):
    """yields a SQLAlchemy engine which is suppressed after the test session"""
    db_url = request.config.getoption("--dburl")
    engine_ = create_engine(db_url, echo=True)

    yield engine_

    engine_.dispose()


@pytest.fixture(scope='session')
def db_session_factory(db_engine):
    """returns a SQLAlchemy scoped session factory"""
    return scoped_session(sessionmaker(bind=db_engine))


@pytest.fixture(scope='function')
def db_session(db_session_factory):
    """yields a SQLAlchemy connection which is rollbacked after the test"""
    session_ = db_session_factory()

    yield session_

    session_.rollback()
    session_.close()
