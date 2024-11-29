import unittest
from unittest.mock import patch, MagicMock, PropertyMock, mock_open
import json
import logging
from utils.blockchain_connector import BlockchainConnector

# Disable the logging for concise output
logging.basicConfig(level=logging.CRITICAL)
class TestBlockchainConnector(unittest.TestCase):
    """
    Tests for the BlockchainConnector class.

    Grouped into:
    - Connection tests
    - Private key tests
    - Derive public address tests
    - Address validation tests
    - Balance retrieval tests
    - Retrieve the latest block number
    """

    """
    Tests for the `connect_to_blockchain` method.
    Scenarios include:
    - Successful connections with Infura and Alchemy
    - Unsupported provider handling
    - Connection failures
    """
    @patch('utils.blockchain_connector.Web3')
    def test_connect_to_blockchain_success_with_infura(self, mock_web3):
        mock_instance = MagicMock()
        mock_instance.is_connected.return_value = True
        mock_web3.return_value = mock_instance

        with patch('utils.blockchain_connector.PROVIDER', 'INFURA'):
            connector = BlockchainConnector()
            self.assertTrue(connector.web3.is_connected())

    @patch('utils.blockchain_connector.Web3')
    def test_connect_to_blockchain_success_with_alchemy(self, mock_web3):
        mock_instance = MagicMock()
        mock_instance.is_connected.return_value = True
        mock_web3.return_value = mock_instance

        with patch('utils.blockchain_connector.PROVIDER', 'ALCHEMY'):
            connector = BlockchainConnector()
            self.assertTrue(connector.web3.is_connected())

    @patch('utils.blockchain_connector.Web3')
    def test_connect_to_blockchain_unsupported_provider(self, mock_web3):
        with patch('utils.blockchain_connector.PROVIDER', 'UNSUPPORTED'):
            with self.assertRaises(ValueError):
                BlockchainConnector()

    @patch('utils.blockchain_connector.Web3')
    def test_connect_to_blockchain_connection_failure(self, mock_web3):
        # Mock Web3 instance with is_connected returning False
        mock_instance = mock_web3.return_value
        mock_instance.is_connected.return_value = False

        with patch('utils.blockchain_connector.PROVIDER', 'INFURA'):
            with self.assertRaises(RuntimeError):
                BlockchainConnector()


    """
    Tests for the `get_valid_private_key` method.
    Scenarios include:
    - Providing a valid private key
    - Handling invalid or missing private keys
    """
    @patch('utils.blockchain_connector.Web3')
    def test_get_valid_private_key_valid_private_key(self, mock_web3):
        with patch('utils.blockchain_connector.PRIVATE_KEY', '0x4c0883a6a102937d6231461b5dbb6204fe512921708279d96ad9e3ef3dbae1fd'):
            connector = BlockchainConnector()
            self.assertIsNotNone(connector.public_address)
            self.assertEqual(connector.private_key, '0x4c0883a6a102937d6231461b5dbb6204fe512921708279d96ad9e3ef3dbae1fd')

    @patch('utils.blockchain_connector.Web3')
    def test_get_valid_private_key_invalid_private_key(self, mock_web3):
        with patch('utils.blockchain_connector.PRIVATE_KEY', 'InvalidPrivateKey'):
            with self.assertRaises(ValueError):
                BlockchainConnector()

    @patch('utils.blockchain_connector.Web3')
    def test_get_valid_private_key_missing_private_key(self, mock_web3):
        with patch('utils.blockchain_connector.PRIVATE_KEY', None):
            with self.assertRaises(ValueError):
                BlockchainConnector()


    """
    Tests for the `derive_public_address` method.
    Scenarios include:
    - Deriving a valid public address from a valid private key
    - Handling an invalid private key
    """
    @patch('utils.blockchain_connector.Web3')
    def test_derive_public_address_success(self, mock_web3):
        # Mock private key and expected public address
        valid_private_key = "0x4c0883a6a102937d6231461b5dbb6204fe512921708279d96ad9e3ef3dbae1fd"
        expected_public_address = "0x0dCbccB685DaD21066Da979e8C32053E7e8F9E9A"

        with patch('utils.blockchain_connector.PRIVATE_KEY', valid_private_key):
            blockchain_connector = BlockchainConnector()
            self.assertEqual(blockchain_connector.public_address, expected_public_address)

    @patch('utils.blockchain_connector.Web3')
    def test_derive_public_address_invalid_key(self, mock_web3):
        # Mock invalid private key
        invalid_private_key = "InvalidPrivateKey"

        with patch('utils.blockchain_connector.PRIVATE_KEY', invalid_private_key):
            with self.assertRaises(ValueError):
                BlockchainConnector()


    """
    Tests for the `load_token_addresses` method.
    Scenarios include:
    - Successfully loading token addresses from a valid JSON file.
    - Handling invalid JSON format.
    - Handling missing or inaccessible files.
    """
    @patch("builtins.open", new_callable=mock_open, read_data='{"USDC": "0x1234", "DAI": "0x5678"}')
    @patch("os.path.join", return_value="config/token_addresses.json")
    def test_load_token_addresses_success(self, mock_path_join, mock_open_file):
        # Initialize BlockchainConnector
        connector = BlockchainConnector()

        # Call the method and assert the result
        result = connector.load_token_addresses()
        expected = {"USDC": "0x1234", "DAI": "0x5678"}
        self.assertEqual(result, expected)
        self.assertTrue(mock_open_file.called)

    @patch("builtins.open", new_callable=mock_open, read_data='Invalid JSON')
    @patch("os.path.join", return_value="config/token_addresses.json")
    def test_load_token_addresses_invalid_json(self, mock_path_join, mock_open_file):
        with self.assertRaises(json.decoder.JSONDecodeError):
            # Initialize BlockchainConnector
            # Method called in init and assert it raises a RuntimeError
            connector = BlockchainConnector()
            

    @patch("os.path.join", return_value="config/token_addresses.json")
    def test_load_token_addresses_file_not_found(self, mock_path_join):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                # Initialize BlockchainConnector
                # Mock open in init to raise a FileNotFoundError
                connector = BlockchainConnector()


    """
    Tests for the `validate_address` method.
    Scenarios include:
    - Validating correctly formatted addresses
    - Handling invalid addresses
    """
    @patch('utils.blockchain_connector.Web3')
    def test_validate_address_valid(self, mock_web3):
        # Mock the is_address method to return True
        mock_instance = mock_web3.return_value
        mock_instance.is_address.return_value = True

        # Initialize the BlockchainConnector
        blockchain_connector = BlockchainConnector()

        # Test with a valid Base address. This is the WETH address.
        valid_address = "0x4200000000000000000000000000000000000006"
        self.assertTrue(blockchain_connector.validate_address(valid_address))

    @patch('utils.blockchain_connector.Web3')
    def test_validate_address_invalid(self, mock_web3):
        # Mock the is_address method to return False
        mock_instance = mock_web3.return_value
        mock_instance.is_address.return_value = False

        # Initialize the BlockchainConnector
        blockchain_connector = BlockchainConnector()

        # Test with an invalid Base address
        invalid_address = "0xInvalidAddress123"
        self.assertFalse(blockchain_connector.validate_address(invalid_address))


    """
    Tests for the `get_balance` method.
    Scenarios include:
    - Retrieving balance for a default address
    - Retrieving balance for custom addresses
    - Handling invalid addresses during balance retrieval
    """
    @patch('utils.blockchain_connector.Web3')
    def test_get_balance_with_default_address(self, mock_web3):
        # Mock the Web3 instance
        mock_instance = mock_web3.return_value
        mock_instance.eth.get_balance.return_value = 1000000000000000000  # 1 Ether in Wei
        mock_instance.from_wei.return_value = 1.0

        # Mock private key and derived public address
        private_key = "0x4c0883a6a102937d6231461b5dbb6204fe512921708279d96ad9e3ef3dbae1fd"
        derived_address = "0x90F8bf6A459f320ead074411a4B0e7943Ea8c9C1"

        # Initialize BlockchainConnector with mocked private key
        with patch('utils.blockchain_connector.PRIVATE_KEY', private_key):
            blockchain_connector = BlockchainConnector()
            blockchain_connector.public_address = derived_address  # Mock public address

        # Call get_balance without specifying an address
        balance = blockchain_connector.get_balance()

        # Assert that the balance for the default address is fetched correctly
        self.assertEqual(balance, 1.0)

    @patch('utils.blockchain_connector.Web3')
    def test_get_balance_with_custom_address(self, mock_web3):
        # Mock the Web3 instance
        mock_instance = mock_web3.return_value
        mock_instance.eth.get_balance.return_value = 2000000000000000000  # 2 Ether in Wei
        mock_instance.from_wei.return_value = 2.0

        # Custom address to test
        custom_address = "0x1234567890abcdef1234567890abcdef12345678"

        # Initialize BlockchainConnector
        blockchain_connector = BlockchainConnector()

        # Call get_balance with a custom address
        balance = blockchain_connector.get_balance(custom_address)

        # Assert that the balance for the custom address is fetched correctly
        self.assertEqual(balance, 2.0)

    @patch('utils.blockchain_connector.Web3')
    def test_get_balance_valid_address(self, mock_web3):
        # Mock the Web3 instance
        mock_instance = mock_web3.return_value
        mock_instance.eth.get_balance.return_value = 1000000000000000000  # 1 Ether in Wei
        mock_instance.from_wei.return_value = 1.0

        # Initialize the BlockchainConnector
        blockchain_connector = BlockchainConnector()

        # Test with a valid Base address
        valid_address = "0x4200000000000000000000000000000000000006"
        balance = blockchain_connector.get_balance(valid_address)

        # Assert the balance is correct
        self.assertEqual(balance, 1.0)

    @patch('utils.blockchain_connector.Web3')
    def test_get_balance_invalid_address(self, mock_web3):
        # Mock the Web3 instance
        mock_instance = mock_web3.return_value
        mock_instance.is_address.return_value = False  # Address validation will fail

        # Initialize the BlockchainConnector
        blockchain_connector = BlockchainConnector()

        # Test with an invalid Base address
        invalid_address = "0xInvalidAddress123"
        balance = blockchain_connector.get_balance(invalid_address)

        # Assert the balance is None for invalid address
        self.assertIsNone(balance)


    """
    Tests for the `get_latest_block_number` method.
    Scenarios include:
    - Successfully retrieving the latest block number
    - Handling errors during retrieval
    """
    @patch('utils.blockchain_connector.Web3')
    def test_get_latest_block_number_success(self, mock_web3):
        # Mock the Web3 instance to return a specific block number
        mock_instance = mock_web3.return_value
        mock_instance.eth.block_number = 12345678

        # Initialize BlockchainConnector
        blockchain_connector = BlockchainConnector()

        # Call get_latest_block_number
        block_number = blockchain_connector.get_latest_block_number()

        # Assert the block number is correct
        self.assertEqual(block_number, 12345678)

    @patch('utils.blockchain_connector.Web3')
    def test_get_latest_block_number_error(self, mock_web3):
        # Mock the Web3 instance
        mock_instance = mock_web3.return_value
        
        # Mock the 'eth' attribute's 'block_number' to raise an exception
        type(mock_instance.eth).block_number = PropertyMock(side_effect=Exception("Error fetching block number"))

        # Initialize BlockchainConnector
        blockchain_connector = BlockchainConnector()

        # Call get_latest_block_number and expect None due to error
        block_number = blockchain_connector.get_latest_block_number()
        self.assertIsNone(block_number)

if __name__ == '__main__':
    # Run the test suite
    unittest.main()
