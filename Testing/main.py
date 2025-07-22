import argparse
import asyncio
import logging

from config import config
from src.osmose.client import OsmoseClient
from src.osmose.content_extractor import ContentExtractor
from src.osmose.metadata_extractor import MetadataExtractor
from src.utils.data_handler import DataHandler

async def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="OSMOSE Data Extraction Tool")
    parser.add_argument(
        "task", 
        choices=["metadata", "content", "all"], 
        help="The task to perform: 'metadata' extraction, 'content' extraction, or 'all'."
    )
    args = parser.parse_args()

    data_handler = DataHandler(config)

    if args.task in ["metadata", "all"]:
        logging.info("Starting metadata extraction task.")
        themes_to_process = data_handler.load_and_process_metadata_input()
        if not themes_to_process.empty:
            async with OsmoseClient(config) as client:
                extractor = MetadataExtractor(config, client)
                await extractor.run(themes_to_process)
            data_handler.consolidate_results()
        logging.info("Metadata extraction task finished.")

    if args.task in ["content", "all"]:
        logging.info("Starting content extraction task.")
        source_data = data_handler.load_and_process_content_input()
        if not source_data.empty:
            async with OsmoseClient(config) as client:
                extractor = ContentExtractor(config, client)
                await extractor.run(source_data)
        logging.info("Content extraction task finished.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    asyncio.run(main()) 