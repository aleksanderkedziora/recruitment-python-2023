import datetime
from abc import ABC, abstractmethod
from typing import Union, Type

import requests
from requests import Response

from task import config
from task.connectors.local.file_reader import ExampleFileReader
from task.setup_loger import setup_loger
from task.utils import Source
from task.validators import validate_config_attr

logger = setup_loger(__name__)


class AbstractCurrencyRateFetcher(ABC):

    def __init__(self, currency: str):
        self._currency = currency
        self._fetch_date = None
        self._rate = None

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def fetch_date(self) -> str:
        if self._fetch_date is None:
            self._set_date()
        return self._fetch_date

    @property
    def rate(self) -> float:
        if self._rate is None:
            self._set_rate()
        return self._rate

    def _set_date(self) -> None:
        self._fetch_date = datetime.date.today().strftime("%Y-%m-%d")

    def _set_rate(self) -> None:
        self._rate = self._retrieve_rate_from_source()

    @abstractmethod
    def _retrieve_rate_from_source(self) -> float:
        """Retrieve currency exchange rate from outer source."""
        raise NotImplementedError()


class LocalSourceCurrencyRateFetcher(AbstractCurrencyRateFetcher):

    def _get_exchange_rate_data_for_currency(self, source_data: dict) -> dict:
        try:
            return source_data[self.currency.upper()]
        except KeyError as e:
            logger.exception('Key error occurred:')
            raise Exception('There is no exchange rate for the specified currency in example file') from e

    def _get_rate(self, currency_data: dict) -> float:  # Note that rates are sorted from newest to oldest items.
        rate_by_date_gen = ((d['date'], d['rate']) for d in currency_data)  # so generator might be better in this case

        rate = None
        for item in rate_by_date_gen:
            if item[0] == self.fetch_date:
                rate = item[1]
                break

        if rate is None:
            msg = 'There is no exchange rate for the specified currency for today in example file'
            logger.error(msg)
            raise KeyError(msg)

        try:
            return float(rate)
        except ValueError:
            logger.exception('ValueError occurred:')
            raise

    def _retrieve_rate_from_source(self) -> float:
        source_data = ExampleFileReader().data

        currency_data = self._get_exchange_rate_data_for_currency(source_data)
        return self._get_rate(currency_data)


class ApiSourceCurrencyRateFetcher(AbstractCurrencyRateFetcher):

    @staticmethod
    def _handle_response_200(response: Response) -> float:
        if 'application/json' in response.headers.get('content-type', ''):
            data = response.json()
            rate = data.get('rates', [{}])[0].get('mid')

            if rate is not None and isinstance(rate, (int, float)):
                logger.info("Currency rate fetched: %s", rate)
                return float(rate)
            else:
                logger.error("Unexpected JSON format: %s", data)
                raise TypeError("Error: Invalid or missing rate in the JSON response")
        else:
            logger.error("Unexpected response content type: %s", response.headers.get('content-type', ''))
            raise TypeError("Error: Unexpected response content type")

    def _handle_response(self, response: Response):

        try:
            response.raise_for_status()
            return self._handle_response_200(response)

        except requests.exceptions.HTTPError:
            logger.exception(f"HTTP error occurred:")
            raise

        except requests.exceptions.RequestException:
            logger.exception(f"Request error occurred:")
            raise

        except Exception:
            logger.exception(f"An unexpected error occurred:")
            raise

    def _get_url(self) -> str:
        return f'http://api.nbp.pl/api/exchangerates/rates/a/{self.currency.lower()}/today/?format = json'

    def _fetch_rate_with_api(self) -> float:
        response = requests.get(self._get_url())
        return self._handle_response(response)

    def _retrieve_rate_from_source(self) -> float:
        return self._fetch_rate_with_api()


@validate_config_attr(Source)
def _get_rate_fetcher_class() -> Type[Union[LocalSourceCurrencyRateFetcher, ApiSourceCurrencyRateFetcher]]:
    if config.RUN_CONFIG['SOURCE'] == Source.LOCAL.value:
        return LocalSourceCurrencyRateFetcher

    return ApiSourceCurrencyRateFetcher


def get_rate_data(currency: str) -> Union[LocalSourceCurrencyRateFetcher, ApiSourceCurrencyRateFetcher]:
    return _get_rate_fetcher_class()(currency)
