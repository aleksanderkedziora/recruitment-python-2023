import json

from task import config


class ExampleFileReader:
    """Converts json to python dict"""

    def __init__(self) -> None:
        self._data = self._read_data()

    @staticmethod
    def _read_data() -> dict:
        with open(config.LOCAL_DATA_SOURCES, "r") as file:
            return json.load(file)

    @property
    def data(self) -> dict:
        return self._data
