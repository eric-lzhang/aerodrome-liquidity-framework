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
    wallet_address = blockchain_connector.public_address
    current_balance = blockchain_connector.get_balance()
    if current_balance is not None:
        logger.info(f"The ETH wallet balance for {wallet_address} is: {current_balance}")
    else:
        logger.error(f"Failed to retrieve the wallet balance for {wallet_address}")

if __name__ == "__main__":
    main()
