import json
from argparse import Namespace

import pytest

from task import config
from task.config import ISO_CODE_BASE
from task.utils import set_run_config, get_iso_codes_list, convert

from decimal import InvalidOperation


@pytest.mark.parametrize('args, expected_mode, expected_source', [
    (Namespace(currency='EUR', price=100.00, prod=True, dev=False, source='API'), 'PROD', 'API'),
    (Namespace(currency='EUR', price=100.00, prod=False, dev=True, source='API'), 'DEV', 'API'),
    (Namespace(currency='EUR', price=100.00, prod=True, dev=False, source='LOCAL'), 'PROD', 'LOCAL'),
    (Namespace(currency='EUR', price=100.00, prod=False, dev=True, source='LOCAL'), 'DEV', 'LOCAL'),
])
def test_set_run_config(clean_config, args, expected_mode, expected_source):
    assert config.RUN_CONFIG['MODE'] == ''
    assert config.RUN_CONFIG['SOURCE'] == ''

    set_run_config(args)

    assert config.RUN_CONFIG['MODE'] == expected_mode
    assert config.RUN_CONFIG['SOURCE'] == expected_source


def test_get_iso_codes_list():
    with open(ISO_CODE_BASE, "r") as file:
        assert get_iso_codes_list() == [d["Symbol waluty (kod ISO)"] for d in json.load(file)]


@pytest.mark.parametrize('arg1, arg2, operator, expected_res', [
    (100.00, 10.00, '*', 1000.00),
    (100.00, 10.00, '/', 10.00)
])
def test_convert_valid(arg1, arg2, operator, expected_res):
    assert convert(price=arg1, rate=arg2, operator=operator) == expected_res


@pytest.mark.parametrize('arg1, arg2, operator, exception, message', [
    (100.00, 0, '/', ZeroDivisionError, "[<class 'decimal.DivisionByZero'>]"),
    ('abc', 'cde', '*', InvalidOperation, "[<class 'decimal.ConversionSyntax'>]"),
    (100.00, 0, '#', Exception, "Invalid operators. Use '*' or '/'."),
])
def test_convert_invalid(arg1, arg2, operator, exception, message):
    with pytest.raises(exception) as excinfo:
        convert(price=arg1, rate=arg2, operator=operator)
    assert str(excinfo.value) == message
