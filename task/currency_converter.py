from dataclasses import dataclass
from typing import ClassVar

from task.connectors.database.sqlite import ConvertedPriceToPLNModel, Base
from task.connectors.database.utils import get_db_connector_class
from task.exchange_rate import get_rate_data
from task.setup_loger import setup_loger
from task.utils import convert

logger = setup_loger(__name__)


@dataclass(frozen=True)
class ConvertedPricePLN:
    """Represents currency conversion operation"""
    price_in_source_currency: float
    currency: str
    currency_rate: float
    currency_rate_fetch_date: str
    price_in_pln: float  # might be stored as Decimal field to avoid floating error points during some calculations.

    bind_db_model: ClassVar[Base] = ConvertedPriceToPLNModel

    def __str__(self):
        return f'{self.price_in_source_currency} {self.currency.upper()} --> {self.price_in_pln} PLN'

    def save(self):
        """Abstraction layer which enables to save cls object independently of run mode"""
        get_db_connector_class()().save(self)
        logger.info(f'Obj {type(self).__name__} ({str(self)}) successfully saved.')

    @classmethod
    def get_all(cls):
        """Abstraction layer which enables to get all cls objects independently of run mode"""
        return get_db_connector_class()().get_all(cls)

    @classmethod
    def get_by_id(cls, id_):
        """Abstraction layer which enables to get cls object, with concrete id, independently of run mode"""
        return get_db_connector_class()().get_by_id(cls, id_)

    def serialize(self):
        """Returns dict in "structure" of databases"""
        return {
            'currency': self.currency,
            'rate': self.currency_rate,
            'price_in_pln': self.price_in_pln,
            'date': self.currency_rate_fetch_date
        }

    @classmethod
    def deserialize(cls, data):
        """Maps "structure of database" dict into class instance"""
        if not isinstance(data, dict):
            data = data.__dict__

        price_in_source_currency = convert(
            price=data['price_in_pln'],
            rate=data['rate'],
            operator='/'
        )

        return ConvertedPricePLN(
            price_in_source_currency=price_in_source_currency,
            currency=data['currency'],
            currency_rate=data['rate'],
            currency_rate_fetch_date=data['date'],
            price_in_pln=data['price_in_pln']
        )


class PriceCurrencyConverterToPLN:
    """Converts wanted price in concrete currency to PLN and saves results in database"""

    def convert_to_pln(self, *, currency: str, price: float) -> ConvertedPricePLN:
        """
        Converts input price in input currency to ConvertedPricePLN instance which represents
        price in pln with some metadata. Conversion is done by multiplying original price by rate
        from API or LOCAL exchange rate source. Finally, function saves ConvertedPricePLN to database
        and returns object at the end.

        :param currency: string ISO currency code
        :param price: price wanted to convert to polish zloty
        :return: ConvertedPricePLN instance
        """
        rate_data = get_rate_data(currency)

        # Used it to avoid floating point error, I think object should 'store' rates and prices as Decimal objs.
        price_in_pln = convert(
            price=price,
            rate=rate_data.rate,
            operator='*'
        )

        converted_price_pln = ConvertedPricePLN(
            price_in_source_currency=price,
            currency=currency.lower(),
            currency_rate=rate_data.rate,
            currency_rate_fetch_date=rate_data.fetch_date,
            price_in_pln=price_in_pln
        )
        converted_price_pln.save()

        return converted_price_pln
