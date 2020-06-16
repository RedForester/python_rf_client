import asyncio
import logging
import os

from rf_api_client import RfApiClient

from rf_client import RfClient

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

MAP_ID = os.getenv('MAP_ID')

logging.basicConfig(level=logging.INFO)

api_client = RfApiClient(
    username=USERNAME,
    password=PASSWORD
)


async def load_map():
    async with RfClient(api_client) as client:
        m = await client.maps.load_map(MAP_ID)
        print('Map name:', m.map_info.name)
        print('Map users:', m.users)
        print('Map types:', m.types)
        print('Root node title:', m.tree.root.body.properties.global_.title)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(load_map())

    loop.run_until_complete(asyncio.sleep(0))
    loop.close()