from typing import Optional
from uuid import uuid4

from rf_api_client import RfApiClient
from rf_api_client.models.nodes_api_models import NodeTreeDto

from rf_client.log import main_logger

PARTIAL_LOAD_LEVELS = 2


async def load_branch(client: RfApiClient, map_id: str, view_root_id: Optional[str]) -> NodeTreeDto:
    logger = main_logger.getChild(str(uuid4()))
    logger.debug(f"Loading branch, map={map_id}, root={view_root_id}")

    root = await client.maps.get_map_nodes(map_id, root_id=view_root_id, level_count=PARTIAL_LOAD_LEVELS)

    async def load_branch(current: NodeTreeDto):
        if not current.meta.leaf and len(current.body.children) == 0:
            logger.debug(f"Loading branch, root={current.id}")
            branch = await client.maps.get_map_nodes(map_id, root_id=current.id, level_count=PARTIAL_LOAD_LEVELS)
            current.body.children = branch.body.children

        for node in current.body.children:
            await load_branch(node)

    await load_branch(root)

    logger.debug("Branch loading completed")
    return root
