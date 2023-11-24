import argparse
import json
from enum import Enum
from typing import Union

from task import config
from task.config import ISO_CODE_BASE

from decimal import Decimal, ROUND_CEILING, InvalidOperation

from task.setup_loger import setup_loger

logger = setup_loger(__name__)


class ExtendedEnum(Enum):
    """Helps with misspelling letters during making condition statements"""

    @classmethod
    def get_value_list(cls):
        return [e.value for e in cls]


class Mode(ExtendedEnum):
    PROD = 'PROD'
    DEV = 'DEV'


class Source(ExtendedEnum):
    API = 'API'
    LOCAL = 'LOCAL'


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Quick currency converter")

    parser.add_argument('currency', type=make_upper, choices=get_iso_codes_list())
    parser.add_argument('price', type=truncate_float, help='Price in the specified currency')

    parser.add_argument('--prod', action='store_true', help='Set mode to production')
    parser.add_argument('--dev', action='store_true', help='Set mode to development')

    parser.add_argument(
        '-s',
        '--source',
        choices=Source.get_value_list(),
        help='Original price source for conversion to PLN (must be "API" or "LOCAL")',
        default=Source.API.value
    )

    return parser


def set_run_config(args) -> None:
    """Sets config dict keys values"""
    mode = Mode.PROD.value
    if args.dev:
        mode = Mode.DEV.value

    config.RUN_CONFIG['MODE'] = mode
    config.RUN_CONFIG['SOURCE'] = args.source


def make_upper(value) -> str:
    return value.upper()


def truncate_float(value):
    try:
        truncated_value = float(value)
        return round(truncated_value, 4)
    except ValueError:
        logger.exception('ValueError occurred:')
        raise
    except Exception:
        logger.exception('An unexpected error occurred:')
        raise


def get_iso_codes_list() -> list:
    """Checks if currency code we pass to CLI is valid (source of iso codes: NBP)"""
    try:
        with open(ISO_CODE_BASE, "r") as file:
            return [d["Symbol waluty (kod ISO)"] for d in json.load(file)]
    except Exception:
        logger.exception('An unexpected error occurred:')
        raise


def convert(rate: float, price: float, operator: str) -> float:
    """Use it to avoid floating-point errors in calculations."""

    try:
        rate_decimal = Decimal(str(rate))
        price_decimal = Decimal(str(price))

        if operator == '*':
            result_decimal = rate_decimal * price_decimal
        elif operator == '/':
            result_decimal = price_decimal / rate_decimal
        else:
            msg = "Invalid operators. Use '*' or '/'."
            logger.error('ValueError occurred. ' + msg)
            raise ValueError(msg)

        result_float = float(result_decimal.quantize(Decimal('.0001'), rounding=ROUND_CEILING))

        return result_float

    except InvalidOperation:
        logger.exception('InvalidOperation occurred:')
        raise

    except ZeroDivisionError:
        logger.exception('ZeroDivisionError occurred:')
        raise

    except Exception:
        logger.exception('An unexpected occurred:')
        raise
