import os
import json
import time
from web3 import Web3
from eth_account import Account
from decimal import Decimal
import logging
from config.config import (
    PROVIDER,
    INFURA_PROJECT_ID,
    PRIVATE_KEY,
    ALCHEMY_PROJECT_ID,
    GAS_AMOUNT
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

    # Core Blockchain Operations
    def __init__(self):
        """
        Initialize the BlockchainConnector by setting up Web3.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.disabled = True # Disable it when necessary
        self.web3 = self.connect_to_blockchain()
        self.private_key = self.get_valid_private_key()
        self.public_address = self.derive_public_address()
        self.token_addresses = self.load_token_addresses()
        self.pools_information = self.load_pools_information() 
    
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


    # Utility Functions
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

            # Create a reverse mapping for address-to-name lookup
            self.token_name_mapping = {v: k for k, v in token_addresses.items()}

            self.logger.info("Token addresses loaded successfully.")
            return token_addresses
        except Exception as e:
            self.logger.error(f"Error loading token addresses: {e}")
            raise

    def load_pools_information(self):
        """
        Loads pool information from a JSON file.

        Returns:
            dict: A dictionary containing information for all pools.

        Raises:
            RuntimeError: If the JSON file cannot be loaded.
        """
        try:
            pools_path = os.path.join("config", "pools_information.json")
            with open(pools_path, 'r') as pools_file:
                pools_information = json.load(pools_file)

            self.logger.info("Pools information loaded successfully.")
            return pools_information
        except Exception as e:
            self.logger.error(f"Error loading pools information: {e}")
            raise RuntimeError("Failed to load pools information.") from e

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

    def to_human_readable(self, amount, decimals):
        """
        Converts a blockchain-compatible amount to a human-readable format.

        Args:
            amount (int): The amount in the smallest unit (e.g., Wei or token smallest unit).
            decimals (int): The number of decimals the token uses (default is 18 for most tokens).

        Returns:
            float: The human-readable amount.
        """
        return float(Decimal(amount) / Decimal(10 ** decimals))

    def to_blockchain_unit(self, amount, decimals):
        """
        Converts a human-readable amount to a blockchain-compatible format.

        Args:
            amount (float): The human-readable amount.
            decimals (int): The number of decimals the token uses (default is 18 for most tokens).

        Returns:
            int: The amount in the smallest unit.
        """
        return int(Decimal(amount) * Decimal(10 ** decimals))


    # Blockchain State Queries
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
        
    def get_token_balance(self, token_address, wallet_address=None):
        """
        Retrieves the balance of a specified token for a given wallet address.

        Args:
            token_address (str): The contract address of the token.
            wallet_address (str, optional): The wallet address to fetch the balance for.
                                            Defaults to the instance's public address.

        Returns:
            float: The balance of the token in human-readable format, or None if an error occurs.
        """
        try:
            # Default to the instance's public address if no wallet address is provided
            if wallet_address is None:
                wallet_address = self.public_address

            # Load the contract
            token_contract = self.load_contract(token_address, "erc20_abi.json")

            # Get token name for logging
            token_name = self.token_name_mapping.get(token_address, "Unknown Token")

            # Fetch the balance and decimals
            balance = token_contract.functions.balanceOf(wallet_address).call()
            decimals = token_contract.functions.decimals().call()

            # Convert balance to human-readable format
            readable_balance = self.to_human_readable(balance, decimals)
            self.logger.info(f"{token_name} balance for {wallet_address}: {readable_balance}")
            return readable_balance

        except Exception as e:
            self.logger.error(f"Error fetching {token_name} balance for {wallet_address}: {e}")
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


    # Transaction-Related Functions
    def approve_token(self, token_address, spender_address, amount=None):
        """
        Approves a spender to spend a specific amount of tokens on behalf of the user.

        Args:
            token_address (str): The contract address of the token.
            spender_address (str): The address of the spender.
            amount (int, optional): The amount of tokens to approve (in the smallest unit). Defaults to the maximum uint256 value.

        Returns:
            str: A message indicating whether approval was granted or not, or the transaction hash if approval was required.

        Raises:
            ValueError: If the token address or spender address is invalid.
            RuntimeError: If the approval transaction fails.
        """
        try:
            # Default to the maximum allowance if no amount is provided
            if amount is None:
                amount = 2**256 - 1  # Maximum value for uint256

            # Validate token and spender addresses
            if not self.validate_address(token_address):
                raise ValueError(f"Invalid token address: {token_address}")
            if not self.validate_address(spender_address):
                raise ValueError(f"Invalid spender address: {spender_address}")

            # Load the token contract
            token_contract = self.load_contract(token_address, "erc20_abi.json")

            # Get token name for logging
            token_name = self.token_name_mapping.get(token_address, "Unknown Token")

            # Check if the current allowance is already enough
            current_allowance = token_contract.functions.allowance(self.public_address, spender_address).call()
            if current_allowance >= amount:
                self.logger.info(f"{token_name} already approved. Current allowance: {current_allowance}")
                return f"Allowance is sufficient. Current allowance: {current_allowance}"

            # Prepare the approval function
            approve_function = token_contract.functions.approve(spender_address, amount)
            
            # Use build_and_send_transaction to handle the transaction
            tx_hash, receipt = self.build_and_send_transaction(approve_function)
            
            self.logger.info(f"Approval successful for {token_name}. Transaction hash: {tx_hash}")
            return f"Approval successful for {token_name}. Transaction hash: {tx_hash}"

        except Exception as e:
            self.logger.error(f"Error during token approval: {e}")
            raise RuntimeError("Token approval transaction failed.") from e

    def build_and_send_transaction(self, transaction_function):
        """
        Builds, signs, and sends a transaction.

        Args:
            transaction_function (function): A callable function from the contract to execute the transaction.
            gas (int): Gas limit for the transaction. Defaults to 200000.
            gas_price_gwei (int): Gas price in Gwei. Defaults to 10.

        Returns:
            str: Transaction hash if the transaction is successful.

        Raises:
            RuntimeError: If an error occurs during transaction building, signing, or sending.
        """
        try:
            # Build the transaction
            transaction = transaction_function.build_transaction({
                'from': self.public_address,
                'gas': GAS_AMOUNT,
                'gasPrice': int(self.web3.eth.gas_price * 1.2),
                'nonce': self.web3.eth.get_transaction_count(self.public_address),
            })

            # Sign the transaction
            signed_tx = self.web3.eth.account.sign_transaction(transaction, private_key=self.private_key)

            # Send the transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            self.logger.info(f"Transaction successful. Hash: {tx_hash.hex()}")
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=1000)

            # Pause to make sure the transaction went through
            time.sleep(1)

            # Check if the transaction is successful
            if receipt.status != 1:
                raise Exception("Minting liquidity failed.")

            return tx_hash.hex(), receipt
        except Exception as e:
            self.logger.error(f"Error during transaction execution: {e}")
            raise RuntimeError("Transaction failed") from e

    def transfer_token(self, token_address, recipient_address, amount):
        """
        Transfers an ERC-20 token from the wallet to a recipient address.

        Args:
            token_address (str): The blockchain address of the token contract.
            recipient_address (str): The blockchain address of the recipient.
            amount (float): The amount of tokens to transfer.

        Returns:
            str: Transaction hash if the transfer is successful.

        Raises:
            ValueError: If any of the addresses or amount is invalid.
        """
        try:
            # Validate addresses
            if not self.validate_address(token_address):
                raise ValueError(f"Invalid token address: {token_address}")
            if not self.validate_address(recipient_address):
                raise ValueError(f"Invalid recipient address: {recipient_address}")

            # Load the ERC-20 contract
            erc20_contract = self.load_contract(token_address, "erc20_abi.json")

            # Get token name for logging
            token_name = self.token_name_mapping.get(token_address, "Unknown Token")

            # Convert the amount to Wei (based on token decimals)
            decimals = erc20_contract.functions.decimals().call()
            amount_in_units = self.to_blockchain_unit(amount, decimals)

            # Set the transaction function
            transaction_function=erc20_contract.functions.transfer(recipient_address, amount_in_units)

            # Use the reusable function to build and send the transaction
            tx_hash = self.build_and_send_transaction(transaction_function)

            self.logger.info(f"Transfer successful for {amount} {token_name} to {recipient_address}. Transaction hash: {tx_hash}")
            return tx_hash
        except Exception as e:
            self.logger.error(f"Error transferring tokens: {e}")
            raise RuntimeError("Transaction failed") from e
