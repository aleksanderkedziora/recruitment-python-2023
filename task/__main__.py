import logging
from logging.config import dictConfig

from task import config
from task.setup_loger import setup_loger

from task.utils import get_parser, set_run_config
from .currency_converter import PriceCurrencyConverterToPLN

logger = setup_loger(__name__)

streamHandler = logging.StreamHandler()
logger.addHandler(streamHandler)


def main(args):
    set_run_config(args)

    logger.info(f"STARTING EXECUTING SCRIPT WITH ARGUMENTS: "
                f"currency: {args.currency},"
                f"price: {args.price},"
                f"source: {config.RUN_CONFIG['SOURCE']},"
                f"mode: {config.RUN_CONFIG['MODE']}")
    try:
        res = PriceCurrencyConverterToPLN().convert_to_pln(
            currency=args.currency,
            price=args.price
        )
        logger.info(f"JOB DONE! The result is {str(res)}\n")
    except Exception as e:
        logger.error(f'{"Conversion failed due to:".upper()} {e}\n')


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args)
