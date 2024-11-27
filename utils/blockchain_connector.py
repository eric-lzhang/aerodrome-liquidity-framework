from web3 import Web3
import logging
from config.config import INFURA_PROJECT_ID

class BlockchainConnector:
    """
    A class to manage the connection to the Base blockchain.

    This class handles:
    - Establishing a Web3 connection using the Infura API.
    - Logging the connection status.
    - Providing utility methods for interacting with the blockchain, such as
      fetching the latest block number.
    
    Attributes:
        logger (logging.Logger): Logger for this class.
        web3 (Web3): Instance of the Web3 connection.
    """

    def __init__(self):
        """
        Initialize the BlockchainConnector by setting up Web3.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.web3 = self.connect_to_blockchain()
    
    def connect_to_blockchain(self):
        """
        Establishes a connection to the Base blockchain using Infura.

        Returns:
            Web3: A Web3 instance connected to the Base network, or None if the connection fails.
        """
        try:
            infura_url = f"https://base-mainnet.infura.io/v3/{INFURA_PROJECT_ID}"
            web3 = Web3(Web3.HTTPProvider(infura_url))

            if web3.is_connected():
                self.logger.info("Successfully connected to the Base blockchain.")
                return web3
            else:
                self.logger.error("Failed to connect to the Base blockchain.")
                return None
        except Exception as e:
            self.logger.error(f"An error occurred while connecting to the Base blockchain: {e}")
            return None

    def get_latest_block_number(self):
        """
        Retrieves the latest block number from the Base blockchain.

        Returns:
            Int: The latest Base block number.
        """
        try:
            latest_block = self.web3.eth.block_number
            self.logger.info(f"Latest Base block number: {latest_block}")
            return latest_block
        except Exception as e:
            self.logger.error(f"Error fetching latest block number: {e}")
            return None

    def validate_address(self, address):
        """
        Validates a Base address.

        Args:
            address (str): The Base address to validate.

        Returns:
            bool: True if the address is valid, False otherwise.
        """
        try:
            is_valid = self.web3.is_address(address)
            if is_valid:
                self.logger.info(f"Valid Base address: {address}")
            else:
                self.logger.warning(f"Invalid Base address: {address}")
            return is_valid
        except Exception as e:
            self.logger.error(f"Error validating address {address}: {e}")
            return False