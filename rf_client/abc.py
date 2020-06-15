import abc
from typing import List

from rf_api_client.models.node_types_api_models import NodeTypeDto
from rf_api_client.models.users_api_models import UserDto


class Map(metaclass=abc.ABCMeta):
    __slots__ = ['id', 'name', 'description', 'root_node_id',
                 'owner', 'owner_username', 'owner_name',
                 'owner_surname', 'owner_avatar', 'layout', 'public',
                 'node_count', 'user_count', 'is_admin']

    @property
    @abc.abstractmethod
    def link(self) -> str:
        """ Прямая ссылка на карту """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def users(self) -> List[UserDto]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def types(self) -> List[NodeTypeDto]:
        raise NotImplementedError


class Tree(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def find(self, func) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def find_one(self, func) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def find_by_id(self, node_id: str) -> str:
        raise NotImplementedError
