from dataclasses import dataclass
from typing import ClassVar

from task import config
from task.connectors.database.json import JsonFileDatabaseConnector
from task.connectors.database.sqlite import SqliteDatabaseConnector, ConvertedPricePLNModel, Base
from task.exchange_rate import get_rate_data


@dataclass(frozen=True)
class ConvertedPricePLN:
    price_in_source_currency: float
    currency: str
    currency_rate: float
    currency_rate_fetch_date: str
    price_in_pln: float

    bind_db_model: ClassVar[Base] = ConvertedPricePLNModel

    def save(self):
        if config.DEV:
            connector_cls = JsonFileDatabaseConnector
        else:
            connector_cls = SqliteDatabaseConnector

        connector_cls().save(self)

    def get_dict_representation(self):
        return {
            'currency': self.currency,
            'rate': self.currency_rate,
            'price_in_pln': self.price_in_pln,
            'date': self.currency_rate_fetch_date
        }


class PriceCurrencyConverterToPLN:

    def convert_to_pln(self, *, currency: str, price: float) -> ConvertedPricePLN:
        rate_data = get_rate_data(currency)

        converted_price_pln = ConvertedPricePLN(
            price_in_source_currency=price,
            currency=currency.lower(),
            currency_rate=rate_data.rate,
            currency_rate_fetch_date=rate_data.fetch_date,
            price_in_pln=float(price) * rate_data.rate
        )
        converted_price_pln.save()

        return converted_price_pln
