from typing import Optional

from rf_api_client import RfApiClient
from rf_api_client.models.nodes_api_models import NodeTreeDto

PARTIAL_LOAD_LEVELS = 2


async def load_branch(client: RfApiClient, map_id: str, view_root_id: Optional[str]) -> NodeTreeDto:
    root = await client.maps.get_map_nodes(map_id, root_id=view_root_id, level_count=PARTIAL_LOAD_LEVELS)

    async def load_branch(current: NodeTreeDto):
        if not current.meta.leaf and len(current.body.children) == 0:
            branch = await client.maps.get_map_nodes(map_id, root_id=current.id, level_count=PARTIAL_LOAD_LEVELS)
            current.body.children = branch.body.children

        for node in current.body.children:
            await load_branch(node)

    await load_branch(root)
    return root
