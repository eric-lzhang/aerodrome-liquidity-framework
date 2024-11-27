# main.py

import logging
from logging_config import setup_logging
from utils.blockchain_connector import BlockchainConnector

def main():
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Initialize Aerodrome Liquidity Framework")

    # Initialize Blockchain Connector
    blockchain_connector = BlockchainConnector()
    latest_block = blockchain_connector.get_latest_block_number()
    if latest_block is not None:
        logger.info(f"Retrieved latest block: {latest_block}")
    else:
        logger.error("Failed to retrieve the latest block.")

if __name__ == "__main__":
    main()
