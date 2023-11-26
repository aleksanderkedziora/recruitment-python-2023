from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Type

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float
)
from sqlalchemy.orm import (
    Session,
    declarative_base
)

from task import config
from task.connectors.database.interface import DBConnectorInterface
from task.setup_loger import setup_loger

if TYPE_CHECKING:
    from task.currency_converter import ConvertedPricePLN

Base = declarative_base()

logger = setup_loger(__name__)


class ConvertedPriceToPLNModel(Base):
    """
    Quasi-proxy Model which is reflection of "dataclass" ConvertedPriceToPLN. It simultaneously keeps structure of
    JSON DB. It also enables to use basic DB query API.
    """
    __tablename__ = 'converted_prices' # noqa

    id = Column(Integer, primary_key=True)
    currency = Column(String)
    rate = Column(Float)
    price_in_pln = Column(Float)  # I think it should be decimal
    date = Column(String)


class SqliteDatabaseConnector(DBConnectorInterface):
    """
    Enables connection and querying for ConvertedPriceToPLN instances (via proxy ConvertedPriceToPLNModel).
    """
    db_url = f'sqlite:///{config.ROOT_DIR}/sqlite3.db'

    def __init__(self):
        self._engine = None
        self._session = None

        db_directory = os.path.dirname(self.db_url.replace('sqlite:///', ''))
        os.makedirs(db_directory, exist_ok=True)

    def _connect(self) -> None:
        """
        Connects to DB if it exists, if not it creates db and then connects.
        """
        self._engine = create_engine(self.db_url, echo=True)
        Base.metadata.create_all(bind=self._engine, checkfirst=True)
        self._session = Session(self._engine)

    def save(self, entity: ConvertedPricePLN) -> None:
        """
        Saves object to Sqlite db.
        """
        self._connect()
        try:
            self._session.add(
                entity.bind_db_model(
                    **entity.serialize()
                )
            )
            self._session.commit()
        except Exception:
            logging.exception('Exception occurred:')
            self._session.rollback()
            raise
        finally:
            self._close_session()

    def get_all(self, entity_cls: Type[ConvertedPricePLN]) -> list[ConvertedPricePLN]:
        """
        Gets all objects for model and converts it to dataclass ConvertedPriceToPLN instances.
        """
        self._connect()
        model_qs = self._session.query(entity_cls.bind_db_model).all()
        return [entity_cls.deserialize(obj) for obj in model_qs]

    def get_by_id(self, entity_cls: Type[ConvertedPricePLN], id_: int) -> ConvertedPricePLN:
        """
        Get object with concrete id for model and converts it to dataclass ConvertedPriceToPLN instance.
        """
        self._connect()
        model_obj = self._session.query(entity_cls.bind_db_model).filter_by(id=id_).first()
        if model_obj is None:
            raise Exception(f'No object {entity_cls.__name__} with id={id_}.')

        return entity_cls.deserialize(model_obj)

    def _close_session(self):
        """Closes db session"""
        self._session.close()
