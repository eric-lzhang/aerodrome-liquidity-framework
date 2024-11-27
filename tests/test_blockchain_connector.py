import unittest
from unittest.mock import patch
import logging
from utils.blockchain_connector import BlockchainConnector

class TestBlockchainConnector(unittest.TestCase):
    @patch('utils.blockchain_connector.Web3')
    def test_connect_to_blockchain_success(self, mock_web3):
        # Mock the Web3 connection
        mock_instance = mock_web3.return_value  # Mock the Web3 instance
        mock_instance.is_connected.return_value = True

        # Initialize the BlockchainConnector
        blockchain_connector = BlockchainConnector()
        
        # Assert the connection was successful
        self.assertTrue(blockchain_connector.web3.is_connected())
    
    @patch('utils.blockchain_connector.Web3')
    def test_connect_to_blockchain_failure(self, mock_web3):
        # Mock the Web3 connection
        mock_instance = mock_web3.return_value  # Mock the Web3 instance
        mock_instance.is_connected.return_value = False

        # Initialize the BlockchainConnector
        blockchain_connector = BlockchainConnector()
        
        # Assert that web3 is None when connection fails
        self.assertIsNone(blockchain_connector.web3)

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

if __name__ == '__main__':
    # Run the test suite
    unittest.main()
