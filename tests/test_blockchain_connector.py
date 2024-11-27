import unittest
from unittest.mock import patch
from utils.blockchain_connector import BlockchainConnector

class TestBlockchainConnector(unittest.TestCase):
    @patch('utils.blockchain_connector.Web3')
    def test_connect_to_blockchain_success(self, mock_web3):
        # Mock the Web3 connection
        mock_web3.return_value.is_connected.return_value = True

        # Initialize the BlockchainConnector
        blockchain_connector = BlockchainConnector()
        
        # Assert the connection was successful
        self.assertTrue(blockchain_connector.web3.is_connected())
    
    @patch('utils.blockchain_connector.Web3')
    def test_connect_to_blockchain_failure(self, mock_web3):
        # Mock the Web3 connection to fail
        mock_web3.return_value.is_connected.return_value = False

        # Initialize the BlockchainConnector
        blockchain_connector = BlockchainConnector()
        
        # Assert the connection was unsuccessful
        self.assertFalse(blockchain_connector.web3.is_connected())

if __name__ == '__main__':
    unittest.main()