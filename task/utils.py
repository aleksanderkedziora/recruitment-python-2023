import argparse
import json
from enum import Enum

from task import config
from task.config import ISO_CODE_BASE


class ExtendedEnum(Enum):

    @classmethod
    def get_value_list(cls):
        return [e.value for e in cls]


class Mode(ExtendedEnum):
    PROD = 'PROD'
    DEV = 'DEV'


class Source(ExtendedEnum):
    API = 'API'
    LOCAL = 'LOCAL'


def get_parser():
    parser = argparse.ArgumentParser(description="Quick currency converter")

    parser.add_argument('currency', type=make_upper, choices=get_iso_codes_list())
    parser.add_argument('price', type=float, help='Price in the specified currency')

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
    mode = Mode.PROD.value
    if args.dev:
        mode = Mode.DEV.value

    config.RUN_CONFIG['MODE'] = mode
    config.RUN_CONFIG['SOURCE'] = args.source


def make_upper(value) -> str:
    return value.upper()


def get_iso_codes_list() -> list:
    try:
        with open(ISO_CODE_BASE, "r") as file:
            return [d["Symbol waluty (kod ISO)"] for d in json.load(file)]
    except Exception:
        raise
