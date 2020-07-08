from rf_api_client import RfApiClient
from rf_api_client.models.nodes_api_models import NodeTreeDto
from rf_event_listener.events import EventVisitor, NodeUpdatedMapEvent, NodeTypeUpdatedMapEvent, NodeCreatedMapEvent, \
    NodeDeletedMapEvent, NodeTaggedMapEvent, NodeUntaggedMapEvent, NodeMovedMapEvent, BranchDeletedMapEvent, \
    BranchMovedMapEvent, CommentPushedMapEvent, CommentDeletedMapEvent, CommentAllReadMapEvent, \
    NodeCopiedMapEvent, BranchCopiedMapEvent, \
    BranchAccessDeniedMapEvent, NodeAccessDeniedMapEvent, BranchAccessGrantedMapEvent, NodeAccessGrantedMapEvent, \
    BranchSubscriptionGrantedMapEvent, BranchSubscriptionDeniedMapEvent, NodeSubscriptionGrantedMapEvent, \
    NodeSubscriptionDeniedMapEvent

from rf_client.partial_loading import load_branch
from rf_client.tree_wrapper import TreeWrapper, NodeWrapper


class ApplyEventVisitor(EventVisitor[None]):
    def __init__(self, client: RfApiClient, map_id: str, tree: TreeWrapper):
        super().__init__(None)
        self._client = client
        self._map_id = map_id
        self._tree = tree

    async def node_updated(self, event: 'NodeUpdatedMapEvent'):
        await self._update_node(event.what)

    async def node_type_updated(self, event: 'NodeTypeUpdatedMapEvent'):
        await self._update_node(event.what)

    async def node_created(self, event: 'NodeCreatedMapEvent'):
        await self._update_node(event.what)

    async def node_deleted(self, event: 'NodeDeletedMapEvent'):
        await self._update_siblings(event.what)

    async def node_tagged(self, event: 'NodeTaggedMapEvent'):
        await self._update_node(event.what)

    async def node_untagged(self, event: 'NodeUntaggedMapEvent'):
        await self._update_node(event.what)

    async def node_moved(self, event: 'NodeMovedMapEvent'):
        new_node = await self._client.maps.get_map_nodes(self._map_id, root_id=event.what, level_count=1)
        await self._update_siblings(event.what)
        self._replace_branch(new_node)

    async def branch_deleted(self, event: 'BranchDeletedMapEvent'):
        await self._update_siblings(event.what)

    async def branch_moved(self, event: 'BranchMovedMapEvent'):
        new_node = await self._client.maps.get_map_nodes(self._map_id, root_id=event.what, level_count=0)
        await self._update_siblings(event.what)
        self._replace_branch(new_node)

    async def comment_pushed(self, event: 'CommentPushedMapEvent'):
        await self._update_node(event.what)

    async def comment_deleted(self, event: 'CommentDeletedMapEvent'):
        await self._update_node(event.what)

    async def comment_all_read(self, event: 'CommentAllReadMapEvent'):
        await self._update_node(event.what)

    async def node_copied(self, event: 'NodeCopiedMapEvent'):
        new_branch = await self._client.maps.get_map_nodes(self._map_id, root_id=event.what, level_count=1)
        self._replace_branch(new_branch)

    async def branch_copied(self, event: 'BranchCopiedMapEvent'):
        new_branch = await load_branch(self._client, self._map_id, event.what)
        self._replace_branch(new_branch)

    async def branch_access_denied(self, event: 'BranchAccessDeniedMapEvent'):
        await self._update_siblings(event.what)

    async def node_access_denied(self, event: 'NodeAccessDeniedMapEvent'):
        await self._update_siblings(event.what)

    async def branch_access_granted(self, event: 'BranchAccessGrantedMapEvent'):
        new_branch = await load_branch(self._client, self._map_id, event.what)
        self._replace_branch(new_branch)

    async def node_access_granted(self, event: 'NodeAccessGrantedMapEvent'):
        await self._update_siblings(event.what)

    async def branch_subscription_granted(self, event: 'BranchSubscriptionGrantedMapEvent'):
        root = self._tree.find_by_id(event.what)
        if not root:
            return
        for node in root.get_all_descendants():
            node.body.meta.subscribed = True

    async def branch_subscription_denied(self, event: 'BranchSubscriptionDeniedMapEvent'):
        root = self._tree.find_by_id(event.what)
        if not root:
            return
        for node in root.get_all_descendants():
            node.body.meta.subscribed = False

    async def node_subscription_granted(self, event: 'NodeSubscriptionGrantedMapEvent'):
        root = self._tree.find_by_id(event.what)
        if not root:
            return
        root.body.meta.subscribed = True

    async def node_subscription_denied(self, event: 'NodeSubscriptionDeniedMapEvent'):
        root = self._tree.find_by_id(event.what)
        if not root:
            return
        root.body.meta.subscribed = False

    async def _update_node(self, node_id: str):
        updated_node = await self._client.maps.get_map_nodes(self._map_id, root_id=node_id, level_count=0)
        self._replace_branch(updated_node)

    async def _update_siblings(self, node_id: str):
        node = self._tree.find_by_id(node_id)
        old_parent = node and node.parent and self._tree.find_by_id(node.parent)
        if old_parent is None:
            return

        new_parent = await self._client.maps.get_map_nodes(self._map_id, root_id=old_parent.id, level_count=1)
        self._replace_branch(new_parent)

    def _replace_branch(self, branch_dto: NodeTreeDto):
        branch = NodeWrapper(**branch_dto.dict())

        # remove node from old parent
        old_node = self._tree.find_by_id(branch.id)
        old_parent_id = old_node and old_node.parent
        old_parent = old_parent_id and self._tree.find_by_id(old_parent_id)
        if old_parent and old_node in old_parent.body.children:
            old_parent.body.children.remove(old_node)

        if not self._is_in_view_root(branch):
            return

        # add node to new parent
        new_parent = self._tree.find_by_id(branch.parent)
        if new_parent:
            new_parent.body.children.append(branch)

        self._replace_node_index_and_children(branch)

    def _replace_node_index_and_children(self, current: NodeWrapper):
        for child in current.body.children:
            self._replace_node_index_and_children(child)

        if not current.meta.leaf and len(current.body.children) == 0:
            old = self._tree.find_by_id(current.id)
            current.body.children = (old and old.body.children) or current.body.children

        for node in self._tree.node_index.values():
            if node.body.id == current.body.id:
                node.body.type_id = current.body.type_id
                node.body.properties = current.body.properties.copy(deep=True)
                node.body.meta = current.body.meta.copy(deep=True)

        self._tree.node_index[current.id] = current
        current._internal_.node_index = self._tree.node_index

    def _is_in_view_root(self, node: NodeTreeDto) -> bool:
        has_loaded_parent = self._tree.find_by_id(node.parent) is not None
        is_root = node.id == self._tree.root.id
        return has_loaded_parent or is_root
