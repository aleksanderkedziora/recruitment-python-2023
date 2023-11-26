import pytest

from task import config
from task.connectors.database.json import JsonFileDatabaseConnector
from task.connectors.database.sqlite import SqliteDatabaseConnector
from task.currency_converter import ConvertedPricePLN, PriceCurrencyConverterToPLN
from task.tests.helpers import with_sqlite_db, with_json_db


@with_sqlite_db
def test_get_all_prod_mode_api(prod_mode, mock_nbp_api):
    converter = PriceCurrencyConverterToPLN()
    res = converter.convert_to_pln(currency='eur', price=105.00)

    connector = SqliteDatabaseConnector()

    queryset = connector.get_all(ConvertedPricePLN)

    for obj in queryset:
        assert isinstance(obj, ConvertedPricePLN)

    model_qs = ConvertedPricePLN.get_all()

    assert model_qs == queryset
    assert res in queryset
    assert res in model_qs


@with_sqlite_db
def test_get_all_prod_mode_local(prod_mode, local_source, temporary_json_file):
    original_filename = config.LOCAL_DATA_SOURCES
    config.LOCAL_DATA_SOURCES = temporary_json_file

    converter = PriceCurrencyConverterToPLN()
    res = converter.convert_to_pln(currency='eur', price=105.00)

    connector = SqliteDatabaseConnector()

    queryset = connector.get_all(ConvertedPricePLN)

    for obj in queryset:
        assert isinstance(obj, ConvertedPricePLN)

    model_qs = ConvertedPricePLN.get_all()

    assert model_qs == queryset
    assert res in queryset
    assert res in model_qs

    config.LOCAL_DATA_SOURCES = original_filename


@with_json_db
def test_get_all_dev_mode_api(dev_mode, mock_nbp_api):
    converter = PriceCurrencyConverterToPLN()
    res = converter.convert_to_pln(currency='eur', price=105.00)

    connector = JsonFileDatabaseConnector()

    queryset = connector.get_all(ConvertedPricePLN)

    for obj in queryset:
        assert isinstance(obj, ConvertedPricePLN)

    model_qs = ConvertedPricePLN.get_all()

    assert model_qs == queryset
    assert res in queryset
    assert res in model_qs


@with_json_db
def test_get_all_dev_mode_local(dev_mode, local_source, temporary_json_file):
    original_filename = config.LOCAL_DATA_SOURCES
    config.LOCAL_DATA_SOURCES = temporary_json_file

    converter = PriceCurrencyConverterToPLN()
    res = converter.convert_to_pln(currency='eur', price=105.00)

    connector = JsonFileDatabaseConnector()

    queryset = connector.get_all(ConvertedPricePLN)

    for obj in queryset:
        assert isinstance(obj, ConvertedPricePLN)

    model_qs = ConvertedPricePLN.get_all()

    assert model_qs == queryset
    assert res in queryset
    assert res in model_qs

    config.LOCAL_DATA_SOURCES = original_filename


@with_sqlite_db
def test_get_by_id_prod_mode_api(prod_mode, mock_nbp_api):
    converter = PriceCurrencyConverterToPLN()
    res = converter.convert_to_pln(currency='eur', price=105.00)

    connector = SqliteDatabaseConnector()

    obj = connector.get_by_id(ConvertedPricePLN, 1)

    assert obj == res


@with_sqlite_db
def test_get_by_id_prod_mode_local(prod_mode, local_source, temporary_json_file):
    original_filename = config.LOCAL_DATA_SOURCES
    config.LOCAL_DATA_SOURCES = temporary_json_file

    converter = PriceCurrencyConverterToPLN()
    res = converter.convert_to_pln(currency='eur', price=105.00)

    connector = SqliteDatabaseConnector()

    obj = connector.get_by_id(ConvertedPricePLN, 1)

    assert obj == res

    config.LOCAL_DATA_SOURCES = original_filename


@with_json_db
def test_get_by_id_dev_mode_api(dev_mode, mock_nbp_api):
    converter = PriceCurrencyConverterToPLN()
    res = converter.convert_to_pln(currency='eur', price=105.00)

    connector = JsonFileDatabaseConnector()

    obj = connector.get_by_id(ConvertedPricePLN, 1)

    assert obj == res


@with_json_db
def test_get_by_id_dev_mode_local(dev_mode, local_source, temporary_json_file):
    original_filename = config.LOCAL_DATA_SOURCES
    config.LOCAL_DATA_SOURCES = temporary_json_file

    converter = PriceCurrencyConverterToPLN()
    res = converter.convert_to_pln(currency='eur', price=105.00)

    connector = JsonFileDatabaseConnector()

    obj = connector.get_by_id(ConvertedPricePLN, 1)

    assert obj == res

    config.LOCAL_DATA_SOURCES = original_filename


@with_sqlite_db
def test_get_by_id_prod_mode_api_invalid(prod_mode, mock_nbp_api):
    converter = PriceCurrencyConverterToPLN()
    converter.convert_to_pln(currency='eur', price=105.00)

    connector = SqliteDatabaseConnector()

    with pytest.raises(Exception) as excinfo:
        connector.get_by_id(ConvertedPricePLN, -1)
    assert excinfo.value.args[0] == 'No object ConvertedPricePLN with id=-1.'


@with_sqlite_db
def test_get_by_id_prod_mode_local(prod_mode, local_source, temporary_json_file):
    original_filename = config.LOCAL_DATA_SOURCES
    config.LOCAL_DATA_SOURCES = temporary_json_file

    converter = PriceCurrencyConverterToPLN()
    converter.convert_to_pln(currency='eur', price=105.00)

    connector = SqliteDatabaseConnector()

    with pytest.raises(Exception) as excinfo:
        connector.get_by_id(ConvertedPricePLN, -1)
    assert excinfo.value.args[0] == 'No object ConvertedPricePLN with id=-1.'

    config.LOCAL_DATA_SOURCES = original_filename


@with_json_db
def test_get_by_id_dev_mode_api(dev_mode, mock_nbp_api):
    converter = PriceCurrencyConverterToPLN()
    converter.convert_to_pln(currency='eur', price=105.00)

    connector = JsonFileDatabaseConnector()

    with pytest.raises(Exception) as excinfo:
        connector.get_by_id(ConvertedPricePLN, -1)
    assert excinfo.value.args[0] == 'No object ConvertedPricePLN with id=-1.'


@with_json_db
def test_get_by_id_dev_mode_local(dev_mode, local_source, temporary_json_file):
    original_filename = config.LOCAL_DATA_SOURCES
    config.LOCAL_DATA_SOURCES = temporary_json_file

    converter = PriceCurrencyConverterToPLN()
    converter.convert_to_pln(currency='eur', price=105.00)

    connector = JsonFileDatabaseConnector()

    with pytest.raises(Exception) as excinfo:
        connector.get_by_id(ConvertedPricePLN, -1)
    assert excinfo.value.args[0] == 'No object ConvertedPricePLN with id=-1.'

    config.LOCAL_DATA_SOURCES = original_filename
