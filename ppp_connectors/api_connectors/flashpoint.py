from typing import Dict, Any, Optional
from ppp_connectors.api_connectors.broker import Broker

class FlashpointConnector(Broker):
    """
    FlashpointConnector provides access to various Flashpoint API search and retrieval endpoints
    using a consistent Broker-based interface.

    Attributes:
        api_key (str): Flashpoint API token used for bearer authentication.
    """
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(base_url="https://api.flashpoint.io", **kwargs)
        self.api_key = api_key or self.env_config.get("FLASHPOINT_API_KEY")
        if not self.api_key:
            raise ValueError("FLASHPOINT_API_KEY is required")
        self.headers.update({
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        })

    def search_communities(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search Flashpoint communities data."""
        return self.post("/sources/v2/communities", json={"query": query, **kwargs}).json()

    def search_fraud(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search Flashpoint fraud datasets."""
        return self.post("/sources/v2/fraud", json={"query": query, **kwargs}).json()

    def search_marketplaces(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search Flashpoint marketplace datasets."""
        return self.post("/sources/v2/markets", json={"query": query, **kwargs}).json()

    def search_media(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search OCR-processed media from Flashpoint."""
        return self.post("/sources/v2/media", json={"query": query, **kwargs}).json()

    def get_media_object(self, media_id: str) -> Dict[str, Any]:
        """Retrieve metadata for a specific media object."""
        return self.get(f"/sources/v2/media/{media_id}").json()

    def get_media_image(self, storage_uri: str) -> Dict[str, Any]:
        """Download image asset by storage_uri."""
        return self.get("/sources/v1/media/", params={"asset_id": storage_uri}).json()
