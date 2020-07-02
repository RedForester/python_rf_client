from typing import Optional, List

from rf_api_client.models.node_types_api_models import NodeTypeDto

from rf_client.tree_wrapper import SearchFunction, NodeWrapper


def match_type_id(type_id: Optional[str]) -> SearchFunction:
    def matcher(node: NodeWrapper):
        return node.body.type_id == type_id
    return matcher


def match_nontyped() -> SearchFunction:
    return match_type_id(None)


def match_none() -> SearchFunction:
    return lambda _: False


def match_type_name(types: List[NodeTypeDto], type_name: str) -> SearchFunction:
    type_ids = [t for t in types if t.name == type_name]
    if len(type_ids) == 0:
        return match_none()
    return match_type_id(type_ids[0].id)


def match_typed_property(key: str, value: str) -> SearchFunction:
    def matcher(node: NodeWrapper):
        return node.body.properties.by_type.get(key, "") == value
    return matcher


def match_all(*matchers: SearchFunction) -> SearchFunction:
    def matcher(node: NodeWrapper):
        return all(m(node) for m in matchers)
    return matcher


def match_any(*matchers: SearchFunction) -> SearchFunction:
    def matcher(node: NodeWrapper):
        return any(m(node) for m in matchers)
    return matcher
