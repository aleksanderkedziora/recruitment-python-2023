import json

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from task import config
from task.connectors.database.sqlite import SqliteDatabaseConnector, ConvertedPriceToPLNModel
from task.currency_converter import PriceCurrencyConverterToPLN, ConvertedPricePLN

from task.tests.helpers import with_sqlite_db, with_json_db


@with_sqlite_db
def test_convert_to_pln_prod_mode_api(prod_mode, mock_nbp_api):

    engine = create_engine(SqliteDatabaseConnector.db_url, echo=True)  # trying to use as basic function as possible
    session = Session(engine)

    counter_before_call = session.query(ConvertedPricePLN.bind_db_model).count()

    converter = PriceCurrencyConverterToPLN()
    res = converter.convert_to_pln(currency='czk', price=105.00)

    engine = create_engine(SqliteDatabaseConnector.db_url, echo=True)  # trying to use as basic function as possible
    session = Session(engine)

    counter_after_call = session.query(ConvertedPricePLN.bind_db_model).count()

    assert isinstance(res, ConvertedPricePLN)
    assert ConvertedPricePLN.bind_db_model is ConvertedPriceToPLNModel
    assert counter_before_call + 1 == counter_after_call


@with_sqlite_db
def test_convert_to_pln_prod_mode_local(prod_mode, local_source, temporary_json_file):
    original_filename = config.LOCAL_DATA_SOURCES
    config.LOCAL_DATA_SOURCES = temporary_json_file

    engine = create_engine(SqliteDatabaseConnector.db_url, echo=True)  # trying to use as basic function as possible
    session = Session(engine)

    counter_before_call = session.query(ConvertedPricePLN.bind_db_model).count()

    converter = PriceCurrencyConverterToPLN()
    res = converter.convert_to_pln(currency='eur', price=105.00)

    engine = create_engine(SqliteDatabaseConnector.db_url, echo=True)  # trying to use as basic function as possible
    session = Session(engine)

    counter_after_call = session.query(ConvertedPricePLN.bind_db_model).count()

    assert isinstance(res, ConvertedPricePLN)
    assert ConvertedPricePLN.bind_db_model is ConvertedPriceToPLNModel
    assert counter_before_call + 1 == counter_after_call

    config.LOCAL_DATA_SOURCES = original_filename


@with_json_db
def test_convert_to_pln_dev_mode_api(dev_mode, mock_nbp_api):

    with open(config.JSON_DATABASE_NAME, "r") as file:
        counter_before_call = len(json.load(file))

    converter = PriceCurrencyConverterToPLN()
    res = converter.convert_to_pln(currency='eur', price=105.00)

    with open(config.JSON_DATABASE_NAME, "r") as file:
        counter_after_call = len(json.load(file))

    assert isinstance(res, ConvertedPricePLN)
    assert ConvertedPricePLN.bind_db_model is ConvertedPriceToPLNModel
    assert counter_before_call + 1 == counter_after_call


@with_json_db
def test_convert_to_pln_dev_mode_local(dev_mode, local_source, temporary_json_file):
    original_filename = config.LOCAL_DATA_SOURCES
    config.LOCAL_DATA_SOURCES = temporary_json_file

    with open(config.JSON_DATABASE_NAME, "r") as file:
        counter_before_call = len(json.load(file))

    converter = PriceCurrencyConverterToPLN()
    res = converter.convert_to_pln(currency='eur', price=105.00)

    with open(config.JSON_DATABASE_NAME, "r") as file:
        counter_after_call = len(json.load(file))

    assert isinstance(res, ConvertedPricePLN)
    assert ConvertedPricePLN.bind_db_model is ConvertedPriceToPLNModel
    assert counter_before_call + 1 == counter_after_call

    config.LOCAL_DATA_SOURCES = original_filename
