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
    """Helper class which helps to get rate and then store it with fetching metadata"""

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
    """Fetcher to get rate for today from example_currency_rates.json file"""

    def _get_exchange_rate_data_for_currency(self, source_data: dict) -> list:
        """
        Due to json file structure it tries to get value for currency ISO code.

        :param source_data: dictionary where keys are currency ISO codes and values are
        list of dicts with keys: date, rate and values for these keys
        :return: list of dicts with keys: date, rate and values for these keys
        """
        try:
            return source_data[self.currency.upper()]
        except KeyError as e:
            logger.exception('Key error occurred:')
            raise Exception('There is no exchange rate for the specified currency in example file') from e

    def _get_rate(self, currency_data: list) -> float:
        """
        Due to json file structure value for currency code key is a list with dicts,
        which stores data about rate and date for it. Note that in json example file values
        are order from newest to oldest, this is the reason why generator is used here.
        We want to get first matching value for date.

        :param currency_data: list of dicts with keys: date, rate and values for these keys
        :return: rate converted to float format
        """

        rate_by_date_gen = ((d['date'], d['rate']) for d in currency_data)  # so generator might be better in this case

        rate = None
        for tup_date, tup_rate in rate_by_date_gen:
            if tup_date == self.fetch_date:
                rate = tup_rate
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
    """Fetcher to get rate for today with NBP API"""

    @staticmethod
    def _handle_response_200(response: Response) -> float:
        """
        Checks if response format is proper and returns wanted rate value

        :param response:
        :return: rate converted to float
        """
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

    def _handle_response(self, response: Response) -> float:
        """
        Checks if response is proper, if it is, it returns rate

        :param response:
        :return: rate converted to float
        """

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
        """Makes request to API url"""
        response = requests.get(self._get_url())
        return self._handle_response(response)

    def _retrieve_rate_from_source(self) -> float:
        return self._fetch_rate_with_api()


@validate_config_attr(Source)
def _get_rate_fetcher_class() -> Type[Union[LocalSourceCurrencyRateFetcher, ApiSourceCurrencyRateFetcher]]:
    """Returns Fetcher class depending on run source"""
    if config.RUN_CONFIG['SOURCE'] == Source.LOCAL.value:
        return LocalSourceCurrencyRateFetcher

    return ApiSourceCurrencyRateFetcher


def get_rate_data(currency: str) -> Union[LocalSourceCurrencyRateFetcher, ApiSourceCurrencyRateFetcher]:
    """Initializes concrete fetcher class instance with currency code input value"""
    return _get_rate_fetcher_class()(currency)
