import datetime
import json
import tempfile

import pytest
import requests

from task import config
from task.exchange_rate import get_rate_data, ApiSourceCurrencyRateFetcher, LocalSourceCurrencyRateFetcher
from requests import Response, HTTPError

from task.tests.helpers import MockResponse


def test_get_rate_data_api_source(api_source, mock_nbp_api):
    currency_code = 'eur'

    rate_data = get_rate_data(currency_code)

    assert isinstance(rate_data, ApiSourceCurrencyRateFetcher)
    assert isinstance(rate_data.rate, float)
    assert rate_data.fetch_date == datetime.date.today().strftime("%Y-%m-%d")
    assert rate_data.currency == currency_code


def test_get_rate_data_api_source_invalid_data(api_source):
    currency_code = 'euro'

    rate_data = get_rate_data(currency_code)

    assert isinstance(rate_data, ApiSourceCurrencyRateFetcher)
    assert rate_data.fetch_date == datetime.date.today().strftime("%Y-%m-%d")
    assert rate_data.currency == currency_code

    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        rate_data.rate # noqa
    assert excinfo.value.args[0] == '404 Client Error: Not Found for url:' \
                                 ' http://api.nbp.pl/api/exchangerates/rates/a/euro/today/?format%20=%20json'


def test_get_rate_data_local_source(local_source, temporary_json_file):
    currency_code = 'eur'

    original_filename = config.LOCAL_DATA_SOURCES
    config.LOCAL_DATA_SOURCES = temporary_json_file

    rate_data = get_rate_data(currency_code)

    assert isinstance(rate_data, LocalSourceCurrencyRateFetcher)
    assert isinstance(rate_data.rate, float)
    assert rate_data.fetch_date == datetime.date.today().strftime("%Y-%m-%d")
    assert rate_data.currency == currency_code

    config.LOCAL_DATA_SOURCES = original_filename


def test_get_rate_data_local_source_invalid_currency(local_source, temporary_json_file):
    currency_code = 'euro'

    original_filename = config.LOCAL_DATA_SOURCES
    config.LOCAL_DATA_SOURCES = temporary_json_file

    rate_data = get_rate_data(currency_code)

    assert isinstance(rate_data, LocalSourceCurrencyRateFetcher)
    assert rate_data.fetch_date == datetime.date.today().strftime("%Y-%m-%d")
    assert rate_data.currency == currency_code

    with pytest.raises(Exception) as excinfo:
        rate_data.rate # noqa
    assert excinfo.value.args[0] == 'There is no exchange rate for the specified currency in example file'

    config.LOCAL_DATA_SOURCES = original_filename


def test_get_rate_data_local_source_invalid_date(local_source, temporary_json_file):
    currency_code = 'czk'

    original_filename = config.LOCAL_DATA_SOURCES
    config.LOCAL_DATA_SOURCES = temporary_json_file

    rate_data = get_rate_data(currency_code)

    assert isinstance(rate_data, LocalSourceCurrencyRateFetcher)
    assert rate_data.fetch_date == datetime.date.today().strftime("%Y-%m-%d")
    assert rate_data.currency == currency_code

    with pytest.raises(Exception) as excinfo:
        rate_data.rate # noqa
    assert excinfo.value.args[0] == 'There is no exchange rate for the specified currency for today in example file'

    config.LOCAL_DATA_SOURCES = original_filename


