import aiohttp
import logging
from typing import Dict, Optional

from config import Config
from src.utils.cookie_manager import AsyncCookieManager

class OsmoseClient:
    """A client for interacting with the Osmose API."""
    def __init__(self, config: Config):
        self._config = config
        self._cookie_manager = AsyncCookieManager(config.OSMOSE_BASE_URL)
        self._session: Optional[aiohttp.ClientSession] = None
        self.cookies: Dict[str, str] = {}

    async def __aenter__(self):
        self.cookies = await self._cookie_manager.reload()
        self._session = aiohttp.ClientSession(
            headers=self._config.REQUEST_HEADERS,
            cookies=self.cookies
        )
        return self

    async def __aexit__(self, exc_type, exc_val, tb):
        if self._session:
            await self._session.close()

    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Performs a GET request."""
        if not self._session:
            raise RuntimeError("Session not started. Use 'async with' statement.")
        return await self._session.get(url, **kwargs)

    async def reload_cookies_and_retry(self):
        """Reloads cookies and updates the session."""
        logging.info("Reloading cookies and updating session...")
        self.cookies = await self._cookie_manager.reload()
        if self._session and not self._session.closed:
            self._session.cookie_jar.clear()
            self._session.cookie_jar.update_cookies(self.cookies)
        else:
            self._session = aiohttp.ClientSession(
                headers=self._config.REQUEST_HEADERS,
                cookies=self.cookies
            ) 