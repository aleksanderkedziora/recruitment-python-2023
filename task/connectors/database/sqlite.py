from __future__ import annotations

import logging
from typing import TYPE_CHECKING

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
from task.setup_loger import setup_loger

if TYPE_CHECKING:
    from task.currency_converter import ConvertedPricePLN

Base = declarative_base()

logger = setup_loger(__name__)


class ConvertedPricePLNModel(Base):
    __tablename__ = 'converted_prices' # noqa

    id = Column(Integer, primary_key=True)
    currency = Column(String)
    rate = Column(Float)
    price_in_pln = Column(Float)
    date = Column(String)


class SqliteDatabaseConnector:
    db_url = f'sqlite:///{config.ROOT_DIR}/sqlite3.db'

    def __init__(self):
        self._engine = None
        self._session = None

    def _connect(self):
        self._engine = create_engine(self.db_url, echo=True)
        self._session = Session(self._engine)

    def save(self, entity: ConvertedPricePLN) -> None:
        self._connect()
        try:
            self._session.add(
                entity.bind_db_model(
                    **entity.get_dict_representation()
                )
            )
            self._session.commit()
        except Exception:
            logging.exception('Exception occurred:')
            self._session.rollback()
            raise
        finally:
            self._close_session()

    def get_all(self, entity: ConvertedPricePLN) -> list[ConvertedPricePLNModel]:
        self._connect()
        return self._session.query(entity.bind_db_model).all()

    def get_by_id(self, entity, id_) -> ConvertedPricePLNModel:
        self._connect()
        return self._session.query(entity.bind_db_model).filter_by(id=id_).first()

    def _close_session(self):
        self._session.close()
