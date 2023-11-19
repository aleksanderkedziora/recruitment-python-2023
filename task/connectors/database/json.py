from __future__ import annotations

from typing import TYPE_CHECKING

import json
from task.config import JSON_DATABASE_NAME

if TYPE_CHECKING:
    from task.currency_converter import ConvertedPricePLN


class JsonFileDatabaseConnector:
    def __init__(self) -> None:
        self._data = self._read_data()

    @staticmethod
    def _read_data() -> dict:
        with open(JSON_DATABASE_NAME, "r") as file:
            return json.load(file)

    def save(self, entity: ConvertedPricePLN) -> int:
        generated_id = self._generate_id()

        data_item = {'id': generated_id}
        data_item.update(entity.get_dict_representation())

        self._data.update({generated_id: data_item})
        self._write_data_to_db()

        return generated_id

    def get_all(self) -> list[...]:
        raise NotImplementedError()

    def get_by_id(self) -> ConvertedPricePLN:
        raise NotImplementedError()

    def _generate_id(self):
        return max((obj['id'] for obj in self._data.values())) + 1

    def _write_data_to_db(self):
        with open(JSON_DATABASE_NAME, 'w') as file:
            json.dump(self._data, file, indent=2)
