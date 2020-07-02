from datetime import datetime
from typing import Optional, Dict

from rf_api_client.models.node_types_api_models import NodeTypeDto
from rf_api_client.models.nodes_api_models import NodeTreeDto, PositionType, NodeAccessType, NodeMetaDto, \
    NodeTreeBodyDto, NodeBodyMetaDto, NodePropertiesDto, GlobalGroupDto, StyleGroupDto

from rf_client.matchers import match_type_id, match_nontyped, match_type_name, match_typed_property, match_all, \
    match_any
from rf_client.tree_wrapper import NodeWrapper


def build_node(
        type_id: Optional[str] = None,
        type_props: Optional[Dict[str, str]] = None,
) -> NodeWrapper:
    node, _ = NodeWrapper.from_tree_dto(
        NodeTreeDto(
            id='node_id',
            map_id='map-id',
            parent=None,
            original_parent=None,
            position=(PositionType.P, '0'),
            access=NodeAccessType.user_all,
            hidden=False,
            readers=[],
            node_level=0,
            meta=NodeMetaDto(
                creation_timestamp=datetime.utcfromtimestamp(0),
                author='',
                last_modified_timestamp=datetime.utcfromtimestamp(0),
                last_modified_user='',
                can_move=True,
                editable=True,
                commentable=True,
                can_set_access=True,
                leaf=True,
            ),
            body=NodeTreeBodyDto(
                id='node_id',
                map_id='map-id',
                type_id=type_id,
                parent=None,
                children=[],
                access=NodeAccessType.user_all,
                unread_comments_count=0,
                comments_count=0,
                readers=[],
                meta=NodeBodyMetaDto(
                    creation_timestamp=datetime.utcfromtimestamp(0),
                    author='',
                    last_modified_timestamp=datetime.utcfromtimestamp(0),
                    last_modified_user='',
                    can_move=True,
                    editable=True,
                    commentable=True,
                    can_set_access=True,
                    subscribed=False,
                ),
                properties=NodePropertiesDto(
                    global_=GlobalGroupDto(
                        title='title',
                    ),
                    by_type=type_props or {},
                    by_user=[],
                    style=StyleGroupDto(),
                    by_extension={},
                ),
            )
        )
    )
    return node


def build_type(type_id: str, type_name: str) -> NodeTypeDto:
    return NodeTypeDto(
        id=type_id,
        name=type_name,
        map_id='map-id',
        icon=None,
        displayable=True,
        default_child_node_type_id=None,
        properties=[],
    )


def test_type_id():
    node = build_node(type_id='test-type')
    assert match_type_id('test-type')(node)
    assert not match_type_id('another-type')(node)


def test_nontyped():
    node = build_node(type_id=None)
    assert match_nontyped()(node)
    assert not match_type_id('type-id')(node)


def test_type_name():
    types = [
        build_type(type_id='first-type', type_name='First'),
        build_type(type_id='second-type', type_name='Second'),
    ]

    first_node = build_node(type_id='first-type')
    assert match_type_name(types, 'First')(first_node)
    assert not match_type_name(types, 'Second')(first_node)
    assert not match_type_name(types, 'Unknown')(first_node)

    second_node = build_node(type_id='second-type')
    assert match_type_name(types, 'Second')(second_node)
    assert not match_type_name(types, 'First')(second_node)
    assert not match_type_name(types, 'Unknown')(second_node)


def test_type_property():
    node = build_node(type_props={
        'Foo': 'Bar',
        'Baz': 'Qux',
    })

    assert match_typed_property('Foo', 'Bar')(node)
    assert match_typed_property('Baz', 'Qux')(node)
    assert not match_typed_property('Foo', '123')(node)
    assert not match_typed_property('Baz', '456')(node)
    assert not match_typed_property('unknown', 'Bar')(node)


def test_all():
    node = build_node(type_id='type-id', type_props={
        'Foo': 'Bar',
        'Baz': 'Qux',
    })

    assert match_all(
        match_type_id('type-id'),
        match_typed_property('Foo', 'Bar'),
    )(node)

    assert match_all(
        match_type_id('type-id'),
        match_typed_property('Foo', 'Bar'),
        match_typed_property('Baz', 'Qux'),
    )(node)

    assert not match_all(
        match_type_id('type-id'),
        match_typed_property('Foo', 'Qux'),
    )(node)

    assert match_all()(node)


def test_any():
    node = build_node(type_id='type-id', type_props={
        'Foo': 'Bar',
        'Baz': 'Qux',
    })

    assert match_any(
        match_type_id('type-id'),
        match_typed_property('Foo', 'Bar'),
    )(node)

    assert match_any(
        match_type_id('type-id'),
        match_typed_property('Foo', 'Bar'),
        match_typed_property('Baz', 'Qux'),
    )(node)

    assert match_any(
        match_type_id('type-id'),
        match_typed_property('Foo', 'Qux'),
    )(node)

    assert not match_any(
        match_type_id('type-id-2'),
        match_typed_property('Foo', 'Qux'),
    )(node)

    assert not match_any()(node)
