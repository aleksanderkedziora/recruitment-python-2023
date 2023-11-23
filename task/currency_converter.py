from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from typing import ClassVar

from task.connectors.database.sqlite import ConvertedPricePLNModel, Base
from task.connectors.database.utils import get_db_connector_class
from task.exchange_rate import get_rate_data
from task.setup_loger import setup_loger

logger = setup_loger(__name__)


@dataclass(frozen=True)
class ConvertedPricePLN:
    price_in_source_currency: float
    currency: str
    currency_rate: float
    currency_rate_fetch_date: str
    price_in_pln: float  # might be stored as Decimal field to avoid floating error points during some calculations.

    bind_db_model: ClassVar[Base] = ConvertedPricePLNModel

    def __str__(self):
        return f'{self.price_in_source_currency} {self.currency.upper()} --> {self.price_in_pln} PLN'

    def save(self):
        get_db_connector_class()().save(self)
        logger.info(f'Obj {type(self).__name__} ({str(self)}) successfully saved.')

    @classmethod
    def get_all(cls):
        model_objs = get_db_connector_class()().get_all(cls)
        return [cls.convert_to_dataclass(obj) for obj in model_objs]

    @classmethod
    def get_by_id(cls, id_):
        model_obj = get_db_connector_class()().get_by_id(cls, id_)
        return cls.convert_to_dataclass(model_obj)

    def get_dict_representation(self):
        return {
            'currency': self.currency,
            'rate': self.currency_rate,
            'price_in_pln': self.price_in_pln,
            'date': self.currency_rate_fetch_date
        }

    @classmethod
    def convert_to_dataclass(cls, data):
        if not isinstance(data, dict):
            data = data.__dict__

        price_in_source_currency = cls._convert(data['rate'], data['price_in_pln'])

        return ConvertedPricePLN(
            price_in_source_currency=price_in_source_currency,
            currency=data['currency'],
            currency_rate=data['rate'],
            currency_rate_fetch_date=data['date'],
            price_in_pln=data['price_in_pln']
        )

    @staticmethod
    def _convert(rate: float, price: float) -> float:
        """Use it to avoid floating point error when calculations."""
        try:
            res = Decimal(str(price)) / Decimal(str(rate))
            return float(res.quantize(Decimal('.0001'), rounding=ROUND_CEILING))

        except InvalidOperation:
            logger.exception('InvalidOperation occurred:')
            raise

        except Exception:
            logger.exception('Exception occurred:')
            raise


class PriceCurrencyConverterToPLN:

    @staticmethod
    def _convert(rate: float, price: float) -> float:
        """Use it to avoid floating point error when calculations."""
        try:
            res = Decimal(str(price)) * Decimal(str(rate))
            return float(res.quantize(Decimal('.0001'), rounding=ROUND_CEILING))

        except InvalidOperation:
            logger.exception('InvalidOperation occurred:')
            raise

        except Exception:
            logger.exception('Exception occurred:')
            raise

    def convert_to_pln(self, *, currency: str, price: float) -> ConvertedPricePLN:
        rate_data = get_rate_data(currency)

        # Used it to avoid floating point error, I think object should 'store' rates and prices as Decimal objs.
        price_in_pln = self._convert(rate_data.rate, price)

        converted_price_pln = ConvertedPricePLN(
            price_in_source_currency=price,
            currency=currency.lower(),
            currency_rate=rate_data.rate,
            currency_rate_fetch_date=rate_data.fetch_date,
            price_in_pln=price_in_pln
        )
        converted_price_pln.save()

        return converted_price_pln
