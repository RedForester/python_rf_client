import asyncio
from typing import List

from rf_api_client import RfApiClient
from rf_api_client.models.node_types_api_models import NodeTypeDto
from rf_api_client.models.users_api_models import UserDto

from rf_client.tree_wrapper import TreeWrapper


class MapWrapper:
    def __init__(self, api_client: RfApiClient, map_id: str, view_root_id: str = None):
        self._api = api_client
        self.__map_id = map_id
        self.__view_root_id = view_root_id

        self.users: List[UserDto] = None
        self.types: List[NodeTypeDto] = None
        self.tree: TreeWrapper = None

    async def load_all(self) -> 'MapWrapper':
        # todo map_info?
        users, types, nodes = await asyncio.gather(
            self._api.maps.get_map_users(self.__map_id),
            self._api.maps.get_map_types(self.__map_id),
            self._api.maps.get_map_nodes(self.__map_id),  # todo view_root_id
        )

        self.users = users  # todo wrap users
        self.types = types  # todo wrap types?
        self.tree = TreeWrapper(nodes)

        return self

    # todo load_info
    # todo load_branch
    # todo load_types
    # todo load_users

    # todo update_info ?

    # todo for standalone usage?
    # async def __aenter__(self):
    #     await asyncio.ensure_future(self.load_all())
    #     return self
    #
    # async def __aexit__(self, exc_type, exc_val, exc_tb):
    #     pass
