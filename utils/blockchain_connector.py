from web3 import Web3
import logging
from config.config import INFURA_PROJECT_ID

class BlockchainConnector:
    """
    A class to manage the connection to the Ethereum blockchain.

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
        Establishes a connection to the Ethereum blockchain using Infura.
        """
        infura_url = f"https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}"
        web3 = Web3(Web3.HTTPProvider(infura_url))
        
        if web3.is_connected():
            self.logger.info("Successfully connected to the Ethereum blockchain.")
        else:
            self.logger.error("Failed to connect to the Ethereum blockchain.")
        
        return web3

    def get_latest_block_number(self):
        """
        Retrieves the latest block number from the Ethereum blockchain.
        """
        try:
            latest_block = self.web3.eth.block_number
            self.logger.info(f"Latest Ethereum block number: {latest_block}")
            return latest_block
        except Exception as e:
            self.logger.error(f"Error fetching latest block number: {e}")
            return None
