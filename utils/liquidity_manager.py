import logging
from utils.blockchain_connector import BlockchainConnector

class LiquidityManager:
    """
    A flexible class to manage liquidity positions.

    This class handles:
    - Supporting multiple liquidity pools by dynamically loading contracts.
    - Managing liquidity positions (open/close).
    """

    def __init__(self, blockchain_connector, abi_filename, contract_address):
        """
        Initialize the LiquidityManager with a blockchain connector, ABI file, and contract address.

        Args:
            blockchain_connector (BlockchainConnector): Instance of the BlockchainConnector class.
            abi_filename (str): Name of the ABI file for the liquidity pool.
            contract_address (str): Address of the liquidity pool contract.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        # self.logger.disabled = True # Disable it when necessary
        self.blockchain_connector = blockchain_connector
        self.abi_filename = abi_filename
        self.contract_address = contract_address
        self.pool_contract = self.blockchain_connector.load_contract(contract_address, abi_filename)
