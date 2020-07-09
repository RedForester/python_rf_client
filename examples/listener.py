import asyncio
import logging
import os
from datetime import datetime

from rf_api_client import RfApiClient
from rf_api_client.rf_api_client import DEFAULT_RF_URL
from rf_event_listener.api import HttpEventsApi
from rf_event_listener.events import TypedMapEvent
from rf_event_listener.listener import MapsListener, EventConsumer

from rf_client import RfClient
from rf_client.map_wrapper import MapWrapper
from rf_client.tree_wrapper import NodeWrapper

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

MAP_ID = os.getenv('MAP_ID')
KV_PREFIX = os.getenv('KV_PREFIX')
VIEW_ROOT_ID = os.getenv('VIEW_ROOT_ID', None)

logging.basicConfig(level=logging.INFO)

api_client = RfApiClient(
    username=USERNAME,
    password=PASSWORD
)

events_api = HttpEventsApi(
    base_url=DEFAULT_RF_URL,
)


def first_line(title: str) -> str:
    try:
        return title.strip().splitlines()[0].strip()
    except IndexError:
        return ''


def print_tree(m: MapWrapper):
    def inner(branch: NodeWrapper, prefix: str = ''):
        print(f'{prefix}{first_line(branch.body.properties.global_.title)} {branch.body.comments_count}')
        for child in branch.body.children:
            inner(child, prefix + '  ')

    inner(m.tree.root)
    count = len(m.tree.node_index)
    print(f'nodes count = {count}')


async def listen():
    client = RfClient(api_client)
    m = await client.maps.load_map(MAP_ID, view_root_id=VIEW_ROOT_ID)

    print_tree(m)

    class Consumer(EventConsumer):
        async def consume(self, timestamp: datetime, event: TypedMapEvent):
            print('Event', event)
            await m.apply_event(event)
            print_tree(m)

    listener = MapsListener(events_api)
    listener.add_map(MAP_ID, KV_PREFIX, Consumer())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(listen())
    loop.run_forever()
