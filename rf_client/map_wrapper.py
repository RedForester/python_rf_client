import asyncio
from typing import Any, List

from rf_api_client import RfApiClient
from rf_api_client.models.maps_api_models import MapDto
from rf_api_client.models.node_types_api_models import NodeTypeDto
from rf_api_client.models.users_api_models import UserDto

from rf_client import TreeWrapper, abc

baseMap = abc.Map


class MapWrapper(baseMap):
    __slots__ = baseMap.__slots__ + ['_client', '_view_root_id', '_users', '_types', '_tree']

    def __init__(self, *, client: RfApiClient, data: MapDto, view_root_id: str = None):
        self._from_data(data)

        self._client = client
        self._view_root_id = view_root_id

        # empty by default
        self._users: List[UserDto] = None
        self._types: List[NodeTypeDto] = None
        self._tree: abc.Tree = None

    def __str__(self):
        return self.name

    def __eq__(self, other: Any):
        return isinstance(other, baseMap) and other.id == self.id

    async def sync(self) -> 'MapWrapper':
        """ Synchronizes all users and types in map """
        types, users, nodes = await asyncio.gather(
            self._client.maps.get_map_types(self.id),
            self._client.maps.get_map_users(self.id),
            self._client.maps.get_map_nodes(self.id)
        )

        self._types = types  # todo wrap types
        self._users = users  # todo wrap users
        self._tree = TreeWrapper(nodes)

        return self

    def _from_data(self, data: MapDto):
        self.id = data.id
        self.name = data.name
        self.description = data.description
        self.root_node_id = data.root_node_id
        self.owner = data.owner
        self.owner_username = data.owner_username
        self.owner_name = data.owner_name
        self.owner_surname = data.owner_surname
        self.owner_avatar = data.owner_avatar
        self.layout = data.layout
        self.public = data.public
        self.node_count = data.node_count
        self.user_count = data.user_count
        self.is_admin = data.is_admin

    @property
    def link(self) -> str:
        return 'https://beta.app.redforester.com/mindmap' \
               f'?mapid=${self.id}'

    @property
    def users(self) -> List[UserDto]:
        if self._users is None:
            raise KeyError('Need to create/sync map')

        return self._users

    @property
    def types(self) -> List[NodeTypeDto]:
        if self._types is None:
            raise KeyError('Need to create/sync map')

        return self._types

    @property
    def tree(self) -> abc.Tree:
        if self._tree is None:
            raise KeyError('Need to create/sync map')

        return self._tree
