from functools import wraps
from rf_api_client import RfApiClient

from rf_client import abc
from rf_client.map_wrapper import MapWrapper


class RfMaps:
    def __init__(self, api: RfApiClient):
        self._api = api

    async def load_map(self, map_id: str, view_root_id: str = None) -> abc.Map:
        data = await self._api.maps.get_map_by_id(map_id)

        return await MapWrapper(
            client=self._api,
            data=data,
            view_root_id=view_root_id
        ).sync()

    # todo get maps list
    # todo create map
    # todo delete map


class Wrapper:
    def __init__(self, api: RfApiClient):
        self._api = api
        self.maps = RfMaps(self._api)

    async def __aenter__(self) -> 'Wrapper':
        await self._api.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._api.__aexit__(exc_type, exc_val, exc_tb)

    def session(self, fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            async with self as session:
                await fn(session, *args, **kwargs)

        return wrapper
