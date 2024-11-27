# main.py

import logging
from logging_config import setup_logging

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Initialize Aerodrome Liquidity Framework")

if __name__ == "__main__":
    main()