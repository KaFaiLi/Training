import asyncio
import itertools
import json
import logging
import os
import time

import aiohttp
import numpy as np
import pandas as pd
from tqdm import tqdm

from config import Config
from src.osmose.client import OsmoseClient

class MetadataExtractor:
    """
    Manages connection to OSMOSE, performs searches, and extracts metadata.
    """
    def __init__(self, config: Config, client: OsmoseClient):
        self.config = config
        self.client = client
        self.error_log = {}

    def _prepare_search_parameters(self, keywords: list) -> list:
        """Generates all combinations of search parameters for API requests."""
        start_days = (self.config.START_DATE - pd.Timestamp("1970-01-01")).days
        end_days = (self.config.END_DATE - pd.Timestamp("1970-01-01")).days
        weekly_start_days = list(range(start_days, end_days, 7))

        directions = ["i", "o", "n"]
        is_attachment = ["true", "false"]
        is_automated = ["true", "false"]

        return list(itertools.product(
            keywords, directions, is_attachment, is_automated, weekly_start_days
        ))

    async def _fetch_url(self, url: str) -> pd.DataFrame:
        """Performs a single GET request and returns a DataFrame or an empty string on failure."""
        try:
            async with self.client.get(url) as response:
                response.raise_for_status()
                json_body = await response.json()
                if "results" in json_body and "results" in json_body["results"]:
                    return pd.DataFrame(json_body["results"]["results"])
                return pd.DataFrame()
        except aiohttp.ClientError as e:
            logging.error(f"Request failed for {url}: {e}")
            return "error"
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON from {url}")
            return "error"

    async def _run_extraction_for_theme(self, process_id: str, keywords: list):
        """Runs the complete extraction process for a single theme."""
        logging.info(f"--- Starting extraction for Process ID: {process_id} ---")
        search_params = self._prepare_search_parameters(keywords)
        if not search_params:
            logging.warning(f"No search parameters generated for {process_id}. Skipping.")
            return

        request_batches = np.array_split(search_params, max(1, len(search_params) // 5))
        
        for i, batch in enumerate(tqdm(request_batches, desc=f"Processing batches for {process_id}")):
            tasks = [self._fetch_url(self._build_url(params)) for params in batch]
            results = await asyncio.gather(*tasks)

            retry_needed = any(res == "error" for res in results)
            if retry_needed:
                logging.info("Failures detected, reloading cookies and retrying batch...")
                await self.client.reload_cookies_and_retry()
                
                tasks_to_retry = [
                    self._fetch_url(self._build_url(params)) 
                    for j, params in enumerate(batch) if results[j] == "error"
                ]
                retry_results = await asyncio.gather(*tasks_to_retry)
                
                final_results = []
                retry_iter = iter(retry_results)
                for res in results:
                    final_results.append(next(retry_iter) if res == "error" else res)
                results = final_results

            valid_results = [df for df in results if isinstance(df, pd.DataFrame) and not df.empty]
            if not valid_results:
                continue

            try:
                batch_df = pd.concat(valid_results, ignore_index=True)
                if not batch_df.empty:
                    batch_df = batch_df.join(pd.json_normalize(batch_df["metadata"])).drop("metadata", axis=1)
                    self._save_results(batch_df, process_id, i)
            except Exception as e:
                logging.error(f"Error processing or saving batch {i} for {process_id}: {e}")
        
        logging.info(f"--- Finished extraction for Process ID: {process_id} ---")

    def _build_url(self, params):
        keyword, direction, attachment, automated, start_day = params
        end_day = start_day + 6
        return (
            f"{self.config.OSMOSE_BASE_URL}api/{self.config.MISSION_ID}/search?n=10000&sort=rel-desc"
            f"&ext={direction}&entitype=Voice&q={keyword}&isAttachment={attachment}"
            f"&isAutomatedMail={automated}&daysSince1970={start_day},{end_day}"
        )

    def _save_results(self, df: pd.DataFrame, process_id: str, batch_number: int):
        """Saves a DataFrame to a compressed CSV file."""
        output_dir = os.path.join(self.config.OUTPUT_PATH_METADATA, process_id)
        os.makedirs(output_dir, exist_ok=True)
        outfile = os.path.join(output_dir, f'{batch_number}.csv.tar.gz')
        try:
            df.to_csv(outfile, index=False, encoding="utf-8-sig", escapechar='\\')
        except (UnicodeDecodeError, UnicodeEncodeError):
            df = df.apply(lambda x: str(x).encode("utf-8-sig", "replace").decode("utf-8-sig"))
            df.to_csv(outfile, index=False, encoding="utf-8-sig", escapechar='\\')
        logging.info(f"Saved results to {outfile}")

    async def run(self, themes_df: pd.DataFrame):
        """Orchestrates the extraction for all selected themes."""
        if themes_df.empty:
            return
            
        for _, theme in themes_df.iterrows():
            process_id = str(theme['Process_ID'])
            keywords = theme['keywords_full_list']
            if not isinstance(keywords, list) or not keywords:
                logging.warning(f"Skipping {process_id} due to missing or invalid keywords.")
                continue
            
            await self._run_extraction_for_theme(process_id, keywords)
        
        logging.info("Full metadata extraction process completed.")
        if self.error_log:
            logging.error("Errors occurred during extraction:")
            for process_id, errors in self.error_log.items():
                if errors:
                    logging.error(f"  {process_id}: {len(errors)} failed requests") 