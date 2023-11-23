from functools import wraps

from task import config
from task.setup_loger import setup_loger

logger = setup_loger(__name__)


def validate_config_attr(enum_cls):
    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            if config.RUN_CONFIG[enum_cls.__name__.upper()] not in enum_cls.get_value_list():
                logger.error(f'Improperly configured RUN_CONFIG attribute. Set proper key-value pair for '
                             f'{enum_cls.__name__.upper()} key.')
                raise Exception('Error with configuration occurred')
            return func(*args, **kwargs)

        return inner_wrapper
    return outer_wrapper
