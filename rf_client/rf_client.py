from typing import Optional

from rf_api_client import RfApiClient

from rf_client.map_wrapper import MapWrapper


class RfMaps:
    def __init__(self, api: RfApiClient):
        self._api = api

    async def load_map(self, map_id: str, view_root_id: Optional[str] = None) -> MapWrapper:
        return await MapWrapper.load_all(
            client=self._api,
            map_id=map_id,
            view_root_id=view_root_id,
        )

    # todo get maps list
    # todo create map
    # todo delete map


class RfClient:
    def __init__(self, api: RfApiClient):
        self._api = api
        self.maps = RfMaps(self._api)

    async def __aenter__(self) -> 'RfClient':
        await self._api.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._api.__aexit__(exc_type, exc_val, exc_tb)
