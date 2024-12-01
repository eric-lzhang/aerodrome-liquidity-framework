import logging
from utils.blockchain_connector import BlockchainConnector

class LiquidityManager:
    """
    A flexible class to manage liquidity positions.

    This class handles:
    - Supporting multiple liquidity pools by dynamically loading contracts.
    - Managing liquidity positions (open/close).
    """

    def __init__(self, pool_name, token0_max, token1_max, lower_range_percentage, upper_range_percentage):
        """
        Initialize the LiquidityManager with parameters and pool information.

        Args:
            pool_name (str): Name of the liquidity pool (e.g., "CL100_WETH_USDC").
            token0_max (float): Maximum amount of token0 (e.g., WETH) to deposit.
            token1_max (float): Maximum amount of token1 (e.g., USDC) to deposit.
            lower_range_percentage (int): Lower range percentage adjustment from the current price.
            upper_range_percentage (int): Upper range percentage adjustment from the current price.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.blockchain_connector = BlockchainConnector()
        
        # Load pool-specific information
        pools_information = self.blockchain_connector.pools_information
        if pool_name not in pools_information:
            raise ValueError(f"Invalid pool name: {pool_name}")

        pool_info = pools_information[pool_name]
        self.token0_name = pool_info["token0"]
        self.token1_name = pool_info["token1"]
        self.pool_contract = self.blockchain_connector.load_contract(pool_info["pool_address"], pool_info["pool_abi"])
        
        # Parameters for liquidity position
        self.token0_max = token0_max
        self.token1_max = token1_max
        self.lower_range_percentage = lower_range_percentage
        self.upper_range_percentage = upper_range_percentage

        self.logger.info(f"Initialized LiquidityManager for pool: {pool_name}")
