import json

from task.config import LOCAL_DATA_SOURCES


class ExampleFileReader:
    def __init__(self) -> None:
        self._data = self._read_data()

    @staticmethod
    def _read_data() -> dict:
        with open(LOCAL_DATA_SOURCES, "r") as file:
            return json.load(file)

    @property
    def data(self) -> dict:
        return self._data
