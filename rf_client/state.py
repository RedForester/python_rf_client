from rf_api_client import RfApiClient


class ConnectionState:
    def __init__(self, client: RfApiClient):
        self.client = client
