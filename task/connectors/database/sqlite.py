from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import Session, declarative_base

from task import config

if TYPE_CHECKING:
    from task.currency_converter import ConvertedPricePLN

Base = declarative_base()


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

    def initialize_db(self):
        engine = create_engine(self.db_url, echo=True)
        Base.metadata.create_all(engine)

    def _connect(self):
        self._engine = create_engine(self.db_url, echo=True)
        self._session = Session(self._engine)

    def save(self, entity: ConvertedPricePLN) -> None:
        self._connect()
        try:
            self._session.add(entity.bind_db_model(**entity.get_dict_representation()))
            self._session.commit()
        except Exception as e:
            print(f"Error during save: {e}")
            self._session.rollback()
        finally:
            self._close_session()

    def _close_session(self):
        self._session.close()
