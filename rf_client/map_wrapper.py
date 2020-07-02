import asyncio
from typing import List, Optional

from rf_api_client import RfApiClient
from rf_api_client.models.maps_api_models import MapDto
from rf_api_client.models.node_types_api_models import NodeTypeDto
from rf_api_client.models.nodes_api_models import NodeTreeDto
from rf_api_client.models.users_api_models import UserDto

from rf_client.log import main_logger as logger
from rf_client.tree_wrapper import TreeWrapper


PARTIAL_LOAD_LEVELS = 2


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

    @classmethod
    async def load_all(cls, *, client: RfApiClient, map_id: str, view_root_id: Optional[str]) -> 'MapWrapper':
        """ Load map users, types and nodes """

        map_info, users, types, nodes = await asyncio.gather(
            client.maps.get_map_by_id(map_id),
            client.maps.get_map_users(map_id),
            client.maps.get_map_types(map_id),
            cls._load_nodes(client, map_id, view_root_id)
        )

        tree = TreeWrapper(nodes)

        return cls(
            client=client,
            map_info=map_info,
            users=users,
            types=types,
            tree=tree
        )

    @classmethod
    async def _load_nodes(cls, client: RfApiClient, map_id: str, view_root_id: Optional[str]) -> NodeTreeDto:
        root = await client.maps.get_map_nodes(map_id, root_id=view_root_id, level_count=PARTIAL_LOAD_LEVELS)

        async def load_branch(current: NodeTreeDto):
            if not current.meta.leaf and len(current.body.children) == 0:
                branch = await client.maps.get_map_nodes(map_id, root_id=current.id, level_count=PARTIAL_LOAD_LEVELS)
                current.body.children = branch.body.children

            for node in current.body.children:
                await load_branch(node)

        await load_branch(root)
        return root
