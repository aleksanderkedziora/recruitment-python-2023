from logging import getLogger

from task import config
from task.connectors.database.sqlite import SqliteDatabaseConnector
from .currency_converter import PriceCurrencyConverterToPLN
import argparse

logger = getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('currency', help='ISO code of currency')
    parser.add_argument('price', help='ISO code of currency')
    parser.add_argument(
        '--mode',
        default='PROD'
    )
    parser.add_argument(
        '-s',
        '--source',
        help='original price which will be converted to PLN',
        default='API'
    )
    return parser


def main(args):
    config.USE_LOCAL = 1 if args.source == 'LOCAL' else 0
    config.DEV = 1 if args.mode == 'DEV' else 0

    if not config.DEV:
        try:
            SqliteDatabaseConnector().initialize_db()
        except Exception as err:
            print(err)

    try:
        PriceCurrencyConverterToPLN().convert_to_pln(
            currency=args.currency,
            price=args.price
        )
        logger.info("Job done!")
    except Exception as err:
        print(err)


if __name__ == "__main__":
    parser = parse_args()
    args = parser.parse_args()
    main(args)
