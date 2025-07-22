import asyncio
import logging
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from typing import Dict

class AsyncCookieManager:
    """Manages authentication cookies using Playwright asynchronously."""
    def __init__(self, url: str):
        self._url = url

    async def reload(self) -> Dict[str, str]:
        """Launches Edge using Playwright to fetch fresh authentication cookies."""
        logging.info("Reloading authentication cookies...")
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(channel="msedge", headless=True)
                context = await browser.new_context(ignore_https_errors=True)
                page = await context.new_page()
                await page.goto(self._url)
                await asyncio.sleep(15)
                cookies = await context.cookies()
                cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
                await browser.close()
                logging.info("Cookies reloaded successfully.")
                return cookies_dict
            except Exception as e:
                logging.error(f"Failed to reload cookies with Playwright: {e}")
                raise

class SyncCookieManager:
    """Manages authentication cookies using Playwright synchronously."""
    def __init__(self, url: str):
        self._url = url

    def reload(self) -> Dict[str, str]:
        """Load cookies by navigating to the specified URL."""
        logging.info("Reloading cookies using Playwright...")
        cookies = self._sync_reload()
        logging.info("Cookies reloaded successfully.")
        return cookies

    def _sync_reload(self) -> Dict[str, str]:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="msedge", headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(self._url)
            asyncio.sleep(20)
            cookies = context.cookies()
        return {cookie['name']: cookie['value'] for cookie in cookies} 