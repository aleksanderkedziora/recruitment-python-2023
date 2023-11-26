from __future__ import annotations

from typing import TYPE_CHECKING

import json

from task import config
from task.connectors.database.interface import DBConnectorInterface

if TYPE_CHECKING:
    from task.currency_converter import ConvertedPricePLN


class JsonFileDatabaseConnector(DBConnectorInterface):
    """Enables to connect and do some operations ond JSON database"""

    def __init__(self) -> None:
        self._data = self._read_data()

    @staticmethod
    def _read_data() -> dict:
        with open(config.JSON_DATABASE_NAME, "r") as file:
            return json.load(file)

    def save(self, entity: ConvertedPricePLN) -> None:  # changed int to None, to keep consistency
        generated_id = self._generate_id()

        data_item = {'id': generated_id}
        data_item.update(entity.serialize())

        self._data.update({generated_id: data_item})
        self._write_data_to_db()

    def get_all(self, entity_cls: [ConvertedPricePLN]) -> list[ConvertedPricePLN]:
        """Gets necessary data from (json) dict and maps into list of ConvertedPricePLN instances"""
        return [entity_cls.deserialize(v) for _, v in self._data.items()]

    def get_by_id(self, entity_cls: [ConvertedPricePLN], id_: int) -> ConvertedPricePLN:
        """Gets necessary data from (json) dict by input id and maps into ConvertedPricePLN instance"""
        obj = [entity_cls.deserialize(v) for _, v in self._data.items() if v['id'] == id_]
        if len(obj) == 0:
            raise Exception(f'No object {entity_cls.__name__} with id={id_}.')

        return obj[0]

    def _generate_id(self) -> int:
        """Generates next id"""
        if self._data.values():
            return max((obj['id'] for obj in self._data.values()))
        return 1

    def _write_data_to_db(self) -> None:
        """Writes self._data to json file"""
        with open(config.JSON_DATABASE_NAME, 'w') as file:
            json.dump(self._data, file, indent=2)
