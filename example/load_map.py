import asyncio
import os

from rf_api_client import RfApiClient
from rf_client import RfClient

client = RfClient(RfApiClient(
    username=os.getenv('USERNAME'),
    password=os.getenv('PWD')
))


async def task_with():
    async with client as c:
        data = await c.maps.load_map(os.getenv('MAP_ID'))
        print(data.users)


loop = asyncio.get_event_loop()

loop.run_until_complete(task_with())
loop.close()
