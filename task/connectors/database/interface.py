from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from task.currency_converter import ConvertedPricePLN


class DBConnectorInterface(ABC):
    """Enables operations on DB"""

    @abstractmethod
    def save(self, entity: ConvertedPricePLN) -> None:
        """
        Get all data and converts it to dataclass ConvertedPriceToPLN instances.

        :param entity: ConvertedPricePLN instance
        :return: None if save is success, otherwise raise exception
        """
        raise NotImplementedError()

    def get_all(self, entity_cls: Type[ConvertedPricePLN]) -> list[ConvertedPricePLN]:
        """
        Get all data and converts it to dataclass ConvertedPriceToPLN instances.

        :param entity_cls: ConvertedPricePLN class
        :return: list of ConvertedPricePLN instances
        """
        raise NotImplementedError()

    def get_by_id(self, entity_cls: Type[ConvertedPricePLN], id_: int) -> ConvertedPricePLN:
        """
        Get data with concrete id and converts it to dataclass ConvertedPriceToPLN instance.

        :param entity_cls: ConvertedPricePLN class
        :param id_: pos integer you want to query with
        :return: ConvertedPricePLN instance
        """
        raise NotImplementedError()
