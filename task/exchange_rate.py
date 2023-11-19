import datetime
from abc import ABC, abstractmethod
from typing import Union

import requests
from requests import Response

from task import config
from task.connectors.local.file_reader import ExampleFileReader


class AbstractCurrencyRateFetcher(ABC):

    def __init__(self, currency: str, fetch_date=None):
        self._currency = currency
        self._fetch_date = None
        self._rate = None

        self._set_date(fetch_date)

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

    def _set_date(self, fetch_date: str = None) -> None:
        self._fetch_date = datetime.date.today().strftime("%Y-%m-%d") if fetch_date is None else fetch_date

    def _set_rate(self) -> None:
        self._rate = self._retrieve_rate_from_source()

    @abstractmethod
    def _retrieve_rate_from_source(self) -> float:
        """Retrieve currency exchange rate from outer source."""
        raise NotImplementedError()


class LocalSourceCurrencyRateFetcher(AbstractCurrencyRateFetcher):

    def _get_exchange_rate_data_for_currency(self, source_data: dict) -> dict:
        try:
            currency_data = source_data[self.currency.upper()]
        except KeyError:
            raise Exception(f'There is no exchange rate for "{self.currency}" code in example file.')

        return currency_data

    def _get_exchange_rate_data_for_date(self, currency_data: dict) -> str:
        try:
            rate = currency_data[self.fetch_date]
        except KeyError:
            raise Exception(f'There is no exchange rate for "{self.currency}" code on "{self.fetch_date}" '
                            f'date in example file.')

        return rate

    def _retrieve_rate_from_source(self) -> float:
        source_data = ExampleFileReader().data

        currency_data = self._get_exchange_rate_data_for_currency(source_data)

        rate_by_date = {d['date']: d['rate'] for d in currency_data}

        rate = self._get_exchange_rate_data_for_date(rate_by_date)

        return float(rate)


class ApiSourceCurrencyRateFetcher(AbstractCurrencyRateFetcher):

    @staticmethod
    def _handle_response(response: Response):

        if response.status_code == 200:
            data = response.json()
            return data['rates'][0]['mid']

        error_messages = {
            404: 'No data for this currency code. Try later, it might be not published yet',
            400: 'Incorrectly prepared service request'
        }

        error_message = error_messages.get(response.status_code)

        if error_message is not None:
            raise Exception(f'{error_message} (status code: {response.status_code}).')
        else:
            raise Exception(f'{response.text} (status code: {response.status_code}).')

    def _get_url(self):
        return f'http://api.nbp.pl/api/exchangerates/rates/a/{self.currency.lower()}/today/?format = json'

    def _fetch(self):
        response = requests.get(self._get_url())
        return self._handle_response(response)

    def _retrieve_rate_from_source(self) -> float:
        return self._fetch()


def get_rate_data(currency: str, fetch_date: str = None) -> Union[LocalSourceCurrencyRateFetcher,
                                                                  ApiSourceCurrencyRateFetcher]:
    if config.USE_LOCAL:
        fetcher_cls = LocalSourceCurrencyRateFetcher
    else:
        fetcher_cls = ApiSourceCurrencyRateFetcher

    fetcher = fetcher_cls(currency, fetch_date)

    return fetcher
