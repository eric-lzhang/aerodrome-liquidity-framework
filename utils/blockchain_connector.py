import os
import json
from web3 import Web3
from eth_account import Account
import logging
from config.config import (
    PROVIDER,
    INFURA_PROJECT_ID,
    PRIVATE_KEY,
    ALCHEMY_PROJECT_ID
)

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
        # self.logger.disabled = True # Disable it when necessary
        self.web3 = self.connect_to_blockchain()
        self.private_key = self.get_valid_private_key()
        self.public_address = self.derive_public_address()
        self.token_addresses = self.load_token_addresses()
    
    def connect_to_blockchain(self):
        """
        Establishes a connection to the Base blockchain using Infura or Alchemy.

        Returns:
            Web3: A Web3 instance connected to the Base network.

        Raises:
            RuntimeError: If the connection to the blockchain fails.
        """
        try:
            # Determine the provider URL
            if PROVIDER == 'INFURA':
                url = f"https://base-mainnet.infura.io/v3/{INFURA_PROJECT_ID}"
                self.logger.info("Using Infura provider.")
            elif PROVIDER == 'ALCHEMY':
                url = f"https://base-mainnet.g.alchemy.com/v2/{ALCHEMY_PROJECT_ID}"
                self.logger.info("Using Alchemy provider.")
            else:
                self.logger.error(f"Unsupported provider '{PROVIDER}' specified in .env.")
                raise ValueError(f"Unsupported provider '{PROVIDER}' specified in .env.")

            # Attempt to connect to the blockchain
            web3 = Web3(Web3.HTTPProvider(url))
            if not web3.is_connected():
                self.logger.error("Failed to connect to the Base blockchain.")
                raise RuntimeError("Failed to connect to the Base blockchain.")

            self.logger.info("Successfully connected to the Base blockchain.")
            return web3
        except Exception as e:
            self.logger.error(f"Error connecting to the blockchain: {e}")
            raise

    def get_valid_private_key(self):
        """
        Retrieves and validates the private key.

        Returns:
            str: A valid private key.

        Raises:
            ValueError: If the private key is invalid or not set.
        """
        if not PRIVATE_KEY:
            self.logger.error("Private key is not set.")
            raise ValueError("Private key is required but not set.")

        try:
            Account.from_key(PRIVATE_KEY)
            return PRIVATE_KEY
        except ValueError as e:
            self.logger.error(f"Invalid private key provided: {e}")
            raise

    def derive_public_address(self):
        """
        Derives the public address from the private key.

        Returns:
            str: The derived public address.

        Raises:
            ValueError: If the private key is not set or an error occurs during derivation.
        """
        try:
            if not self.private_key:
                self.logger.error("Private key is not set.")
                raise ValueError("Private key is required but not set.")

            account = Account.from_key(self.private_key)
            public_address = account.address
            self.logger.info(f"Derived public address: {public_address}")
            return public_address
        except Exception as e:
            self.logger.error(f"Error deriving public address: {e}")
            raise

    def load_token_addresses(self):
        """
        Loads token addresses from a JSON file.

        Returns:
            dict: A dictionary mapping token names to addresses.

        Raises:
            RuntimeError: If the JSON file cannot be loaded.
        """
        try:
            tokens_path = os.path.join("config", "token_addresses.json")
            with open(tokens_path, 'r') as tokens_file:
                token_addresses = json.load(tokens_file)
            self.logger.info("Token addresses loaded successfully.")
            return token_addresses
        except Exception as e:
            self.logger.error(f"Error loading token addresses: {e}")
            raise

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

    def load_contract(self, contract_address, abi_filename):
        """
        Loads a smart contract instance given its address and ABI file.

        Args:
            contract_address (str): The blockchain address of the contract.
            abi_filename (str): The name of the ABI JSON file (without the path).

        Returns:
            web3.eth.Contract: The loaded contract instance.

        Raises:
            ValueError: If the contract address is invalid or the ABI file cannot be loaded.
        """
        try:
            # Validate the contract address
            if not self.validate_address(contract_address):
                raise ValueError(f"Invalid contract address: {contract_address}")

            # Construct the path to the ABI file
            abi_path = os.path.join("config", "abi", abi_filename)
            with open(abi_path, "r") as abi_file:
                contract_abi = json.load(abi_file)

            # Return the contract instance
            contract = self.web3.eth.contract(address=contract_address, abi=contract_abi)
            self.logger.info(f"Loaded contract at address: {contract_address}")
            return contract

        except FileNotFoundError:
            self.logger.error(f"ABI file not found: {abi_filename}")
            raise ValueError("ABI file not found.")
        except ValueError as ve:
            self.logger.error(f"ValueError: {ve}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error loading contract: {e}")
            raise

    def get_balance(self, address=None):
        """
        Retrieves the balance of the specified Base address.

        Args:
            address (str): The Base address to check the balance for.

        Returns:
            float: The balance in Ether, or None if an error occurs.
        """
        try:
            # Use the instance's public address if no address is provided
            if address is None:
                address = self.public_address

            if not self.validate_address(address):
                self.logger.error(f"Invalid Base address: {address}")
                return None

            # Retrieve the balance in Wei and convert to Ether
            balance_wei = self.web3.eth.get_balance(address)
            balance_ether = self.web3.from_wei(balance_wei, 'ether')
            self.logger.info(f"Balance for address {address}: {balance_ether} Ether")
            return balance_ether
        except Exception as e:
            self.logger.error(f"Error retrieving balance for address {address}: {e}")
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
