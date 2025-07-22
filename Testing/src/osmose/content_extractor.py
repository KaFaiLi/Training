import asyncio
import csv
import logging
import os
import time
from typing import Any, Dict, List, Optional

import pandas as pd
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from tqdm.asyncio import tqdm

from config import Config
from src.osmose.client import OsmoseClient
from src.utils.rate_limiter import RateLimiter


class ContentFetcher:
    """Handles fetching web content with retries and cookie management."""
    def __init__(self, config: Config, client: OsmoseClient, rate_limiter: RateLimiter):
        self._config = config
        self._client = client
        self._rate_limiter = rate_limiter

    async def get_content(self, url: str, retries: int = 5) -> Optional[bytes]:
        """Fetches content from a URL with retry logic."""
        for attempt in range(retries):
            try:
                async with self._rate_limiter:
                    async with self._client.get(url, timeout=25) as response:
                        logging.info(f"Attempt {attempt+1} for URL: {url}; Status: {response.status}")
                        if response.status == 200:
                            return await response.read()
                        
                        error_text = await response.text()
                        logging.error(f"Unexpected status {response.status} for {url}. Response: {error_text}")
                        if 400 <= response.status < 500:
                           break
            except Exception as e:
                logging.error(f"Attempt {attempt+1} failed for {url}. Error: {e}")

            if attempt == 1 and attempt < retries - 1:
                logging.info("Second attempt failed. Reloading cookies before next retry.")
                await self._client.reload_cookies_and_retry()

            if attempt < retries - 1:
                wait_time = 2 ** attempt
                logging.info(f"Waiting for {wait_time}s before retrying...")
                await asyncio.sleep(wait_time)
        
        logging.error(f"Exhausted all retries for URL: {url}")
        return None


class RowProcessor:
    """Processes a single data row: fetches, parses, and saves content."""
    def __init__(self, fetcher: ContentFetcher, output_dir: str):
        self._fetcher = fetcher
        self._output_dir = output_dir

    async def process(self, row_data: pd.Series) -> Optional[Dict[str, Any]]:
        """Processes a single row from the input data."""
        url = row_data.get('URL', '')
        if not url:
            logging.warning(f"No URL for DATE: {row_data['DATE']} and Keyword: {row_data['Keyword']}")
            return None

        content = await self._fetcher.get_content(url)
        if content is None:
            logging.error(f"Failed to fetch url: {url}, Skipping DATE: {row_data['DATE']} and Keyword: {row_data['Keyword']}")
            return None

        soup = BeautifulSoup(content, 'html.parser')

        date_keyword_folder = os.path.join(self._output_dir, f"{row_data['DATE']}_{row_data['Keyword']}")
        os.makedirs(date_keyword_folder, exist_ok=True)

        unique_filename = f"{row_data['msgId'] if row_data['msgId'] else int(time.time() * 1000)}.html"
        html_file_path = os.path.join(date_keyword_folder, unique_filename)
        try:
            with open(html_file_path, "w", encoding="utf-8") as html_file:
                html_file.write(soup.prettify())
        except IOError as e:
            logging.error(f"Error saving HTML file for URL: {url}. Error: {e}")
            return None

        markdown_content = md(str(soup))
        return {
            "DATE": row_data["DATE"],
            "Keyword": row_data["Keyword"],
            "msgId": row_data["msgId"],
            "isAttachment": row_data["isAttachment"],
            "Title": row_data["Title_eng"],
            "Extension": row_data["extension"],
            "URL": url,
            "HTML File Path": html_file_path,
            "Content": markdown_content
        }


class ContentExtractor:
    """Orchestrates the entire content extraction process."""
    def __init__(self, config: Config, client: OsmoseClient):
        self._config = config
        self._client = client
        self._setup_logging()
        os.makedirs(self._config.OUTPUT_PATH_CONTENT, exist_ok=True)

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self._config.LOG_FILENAME, mode='w', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

    def _save_results(self, results: List[Dict[str, Any]]):
        """Saves the extracted content to CSV and Excel files."""
        if not results:
            logging.warning("No results to save.")
            return

        results_df = pd.DataFrame(results)
        base_filename = os.path.basename(self._config.INPUT_FILE_CONTENT)
        filename_without_ext = os.path.splitext(base_filename)[0]

        csv_output_path = f"Content_extract_{filename_without_ext}.csv"
        excel_output_path = os.path.join(self._config.OUTPUT_PATH_CONTENT, f"{filename_without_ext}_Content_Extract.xlsx")

        try:
            results_df.to_csv(
                csv_output_path,
                index=False,
                sep='\t',
                encoding='utf-8-sig',
                quoting=csv.QUOTE_ALL
            )
            logging.info(f"Exported results to CSV: {csv_output_path}")

            results_df.to_excel(excel_output_path, index=False, engine='openpyxl')
            logging.info(f"Exported results to Excel: {excel_output_path}")
        except Exception as e:
            logging.error(f"Error saving output files: {e}")

    async def run(self, source_data: pd.DataFrame):
        """Executes the full extraction pipeline."""
        if source_data is None or source_data.empty:
            logging.error("Halting execution due to data loading issues.")
            return

        rate_limiter = RateLimiter(self._config.RATE_LIMIT_MAX_CALLS, self._config.RATE_LIMIT_PERIOD_SECONDS)
        concurrency_semaphore = asyncio.Semaphore(self._config.MAX_CONCURRENT_REQUESTS)

        fetcher = ContentFetcher(self._config, self._client, rate_limiter)
        processor = RowProcessor(fetcher, self._config.OUTPUT_PATH_CONTENT)
        
        async def process_with_semaphore(row):
            async with concurrency_semaphore:
                return await processor.process(row)

        tasks = [
            asyncio.create_task(process_with_semaphore(row))
            for _, row in source_data.iterrows()
        ]

        results = []
        progress_bar = tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Processing rows")
        for future in progress_bar:
            try:
                result = await future
                if result:
                    results.append(result)
            except Exception as e:
                logging.error(f"Error processing a row task: {e}")

        self._save_results(results) 