import asyncio
from typing import List, Optional

from rf_api_client import RfApiClient
from rf_api_client.models.maps_api_models import MapDto
from rf_api_client.models.node_types_api_models import NodeTypeDto
from rf_api_client.models.users_api_models import UserDto
from rf_event_listener.events import TypedMapEvent

from rf_client.event_visitor import ApplyEventVisitor
from rf_client.log import main_logger as logger
from rf_client.partial_loading import load_branch
from rf_client.tree_wrapper import TreeWrapper


class MapWrapper:
    def __init__(
            self,
            *,
            client: RfApiClient,
            map_info: MapDto,
            users: List[UserDto],
            types: List[NodeTypeDto],
            tree: TreeWrapper,
    ):
        self._client = client
        self.map_info = map_info
        self.users = users
        self.types = types
        self.tree = tree

        logger.info(f'Init MapWrapper for map {map_info.id}')  # todo view_root_id = {view_root_id}

    async def apply_event(self, event: TypedMapEvent):
        await event.visit(ApplyEventVisitor(self._client, self.map_info.id, self.tree))

    @classmethod
    async def load_all(cls, *, client: RfApiClient, map_id: str, view_root_id: Optional[str]) -> 'MapWrapper':
        """ Load map users, types and nodes """

        map_info, users, types, nodes = await asyncio.gather(
            client.maps.get_map_by_id(map_id),
            client.maps.get_map_users(map_id),
            client.maps.get_map_types(map_id),
            load_branch(client, map_id, view_root_id)
        )

        tree = TreeWrapper(nodes)

        return cls(
            client=client,
            map_info=map_info,
            users=users,
            types=types,
            tree=tree
        )
