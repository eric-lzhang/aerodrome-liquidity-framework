import logging
import time
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
            lower_range_percentage (int): Percentage adjustment below the current tick for the lower range. 
                                        A positive value (e.g., 1 for 1%) expands the range downward.
            upper_range_percentage (int): Percentage adjustment above the current tick for the upper range. 
                                        A positive value (e.g., 1 for 1%) expands the range upward.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.disabled = True # Disable it when necessary

        self.blockchain_connector = BlockchainConnector()
        
        # Load pool-specific information
        pools_information = self.blockchain_connector.pools_information
        if pool_name not in pools_information:
            raise ValueError(f"Invalid pool name: {pool_name}")

        self.pool_info = pools_information[pool_name]
        self.token0_name = self.pool_info["token0"]
        self.token1_name = self.pool_info["token1"]
        self.pool_address = self.pool_info["pool_address"]
        self.pool_contract = self.blockchain_connector.load_contract(self.pool_address, self.pool_info["pool_abi"])
        self.nft_address = self.pool_info["nft_address"]
        self.nft_contract = self.blockchain_connector.load_contract(self.nft_address, self.pool_info["nft_abi"])
        
        # Load token contracts to fetch decimals
        self.token0_address = self.blockchain_connector.token_addresses[self.token0_name]
        self.token1_address = self.blockchain_connector.token_addresses[self.token1_name]
        self.token0_contract = self.blockchain_connector.load_contract(self.token0_address, "erc20_abi.json")
        self.token1_contract = self.blockchain_connector.load_contract(self.token1_address, "erc20_abi.json")
        
        # Store decimals
        self.token0_decimals = self.token0_contract.functions.decimals().call()
        self.token1_decimals = self.token1_contract.functions.decimals().call()

        # Parameters for liquidity position
        self.token0_max = token0_max
        self.token1_max = token1_max
        self.lower_range_percentage = lower_range_percentage
        self.upper_range_percentage = upper_range_percentage

        self.logger.info(f"Initialized LiquidityManager for pool: {pool_name}")

    def tick_to_price(self, tick):
        """
        Converts a tick value to the corresponding price.

        Args:
            tick (int): The tick value to convert.

        Returns:
            float: The price corresponding to the tick.
        """
        try:
            base = 1.0001
            adjusted_decimal = 10 ** (self.token0_decimals - self.token1_decimals)
            price = (base ** tick) * adjusted_decimal
            return price
        except Exception as e:
            self.logger.error(f"Error converting tick to price: {e}")
            raise RuntimeError("Failed to convert tick to price.") from e

    def get_current_price(self):
        """
        Retrieves the current price of token0 in terms of token1.

        Returns:
            float: The current price of token0 in terms of token1.

        Raises:
            RuntimeError: If fetching the current price fails.
        """
        try:
            # Fetch the current sqrt price from the pool
            slot0 = self.pool_contract.functions.slot0().call()
            sqrt_price_x96 = slot0[0]
            ratio = (sqrt_price_x96 / (1 << 96)) ** 2
            adjusted_decimal = 10 ** (self.token0_decimals - self.token1_decimals)
            current_price = ratio * adjusted_decimal
            self.logger.info(f"Current price: {current_price}")
            return current_price
        except Exception as e:
            self.logger.error(f"Failed to get current price: {e}")
            raise RuntimeError("Failed to fetch current price.") from e

    def get_pool_status(self):
        """
        Retrieve the current status of the liquidity pool.

        This includes:
        - Current tick
        - Adjusted lower and upper ticks based on specified percentage ranges
        - Current price, lower price, and upper price in the pool

        Returns:
            dict: A dictionary with the following keys:
                - current_tick: The current tick of the pool.
                - lower_tick: The adjusted lower tick.
                - upper_tick: The adjusted upper tick.
                - current_price: The current price of token0 in terms of token1.
                - lower_price: The price corresponding to the lower tick.
                - upper_price: The price corresponding to the upper tick.

        Raises:
            RuntimeError: If fetching the pool status fails.
        """
        try:
            slot0 = self.pool_contract.functions.slot0().call()

            # Calculate the lower and upper ticks with adjustments
            current_tick = int(slot0[1])
            self.tick_spacing = self.pool_contract.functions.tickSpacing().call()

            # The raw tick represent the narrowest tick range that contains the current tick
            raw_lower_tick = current_tick - (current_tick % self.tick_spacing)
            raw_upper_tick = raw_lower_tick + self.tick_spacing
            
            # Adjust the raw ticks based on the specified range percentages
            lower_tick = raw_lower_tick - self.lower_range_percentage * self.tick_spacing
            upper_tick = raw_upper_tick + self.upper_range_percentage * self.tick_spacing

            
            # Calculate prices
            current_price = self.get_current_price()
            lower_price = self.tick_to_price(lower_tick)
            upper_price = self.tick_to_price(upper_tick)

            status = {
                "current_price": current_price,
                "lower_price": lower_price,
                "upper_price": upper_price,
                "current_tick": current_tick,
                "lower_tick": lower_tick,
                "upper_tick": upper_tick,
            }

            return status

        except Exception as e:
            self.logger.error(f"Failed to get pool status: {e}")
            raise RuntimeError("Failed to fetch pool status.") from e

    def open_liquidity_position(self):
        """
        Opens a liquidity position in the pool with the specified parameters.

        This function:
        - Approves token0 and token1 spending.
        - Calculates the tick range and amounts for the liquidity position.
        - Mints a liquidity position in the pool.

        Returns:
            str: Transaction hash of the mint operation.

        Raises:
            RuntimeError: If opening the liquidity position fails.
        """
        try:
            # Get pool status to determine ticks and price range
            self.start_pool_status = self.get_pool_status()
            lower_tick = self.start_pool_status["lower_tick"]
            upper_tick = self.start_pool_status["upper_tick"]
            
            # Convert human-readable token amounts to blockchain units
            token0_amount = self.blockchain_connector.to_blockchain_unit(self.token0_max, self.token0_decimals)
            token1_amount = self.blockchain_connector.to_blockchain_unit(self.token1_max, self.token1_decimals)

            # Approve token spending for the pool contract
            self.blockchain_connector.approve_token(self.token0_address, self.nft_address, token0_amount)
            self.blockchain_connector.approve_token(self.token1_address, self.nft_address, token1_amount)

            # Prepare mint parameters
            mint_parameters = {
                "token0": self.token0_address,
                "token1": self.token1_address,
                'tickSpacing': self.tick_spacing,
                "tickLower": lower_tick,
                "tickUpper": upper_tick,
                "amount0Desired": token0_amount,
                "amount1Desired": token1_amount,
                "amount0Min": 0,  # Set minimums to zero for simplicity
                "amount1Min": 0,
                "recipient": self.blockchain_connector.public_address,
                "deadline": self.blockchain_connector.web3.eth.get_block("latest")["timestamp"] + 3 * 60,  # Deadline 3 minute from now
                'sqrtPriceX96': 0
            }

            # Call the pool contract to mint liquidity position
            mint_function = self.nft_contract.functions.mint(mint_parameters)

            # Build and send the transaction
            self.opening_tx_hash, self.opening_receipt = self.blockchain_connector.build_and_send_transaction(mint_function)
            
            # Parse the opening receipt to store the liquidity position data
            self.parse_opening_receipt()

            self.logger.info(f"Liquidity position opened successfully. Transaction hash: {self.opening_tx_hash}")
            return self.opening_tx_hash

        except Exception as e:
            self.logger.error(f"Failed to open liquidity position: {e}")
            raise RuntimeError("Failed to open liquidity position.") from e

    def parse_opening_receipt(self):
        """
        Parses a opening receipt to extract amount0, amount1, and nft token id.

        Args:
            receipt (dict): The transaction receipt obtained from the blockchain.

        Returns:
            dict: A dictionary containing amount0, amount1, and nft token id.
        """
        try:
            # Iterate through the logs to find the relevant data
            for log in self.opening_receipt["logs"]:
                # Get the amount0
                if log.address == self.token0_address:
                    raw_amount0_hex = log.data.hex()
                    raw_amount0 = int(raw_amount0_hex, 16)
                    self.amount0 = self.blockchain_connector.to_human_readable(raw_amount0, self.token0_decimals)
                
                # Get the amount1
                if log.address == self.token1_address:
                    raw_amount1_hex = log.data.hex()
                    raw_amount1 = int(raw_amount1_hex, 16)
                    self.amount1 = self.blockchain_connector.to_human_readable(raw_amount1, self.token1_decimals)

                # Get the nft token id
                # There are two log addresses equal to the nft address, we use this to find the one we need
                if log.address == self.nft_address and len(log.topics) == 2: # There are two log addresses equal to the nft address, we use this to find the one we need
                    token_id_hex = log.topics[1].hex()
                    self.nft_token_id = int(token_id_hex, 16)

            # Return the parsed results in a dictionary
            return {
                "amount0": self.amount0,
                "amount1": self.amount1,
                "tokenId": self.nft_token_id,
            }

        except Exception as e:
            raise RuntimeError(f"Error parsing mint receipt: {e}")

    def close_liquidity_position(self, amount0Min=0, amount1Min=0, amount0Max=2**128 - 1, amount1Max=2**128 - 1):
        """
        Closes the liquidity position by:
        - Decreasing liquidity to release tokens.
        - Collecting accrued fees.
        - Burning the NFT associated with the liquidity position.

        Args:
            amount0Min (int, optional): Minimum amount of token0 to receive when decreasing liquidity. Defaults to 0.
            amount1Min (int, optional): Minimum amount of token1 to receive when decreasing liquidity. Defaults to 0.
            amount0Max (int, optional): Maximum amount of token0 to collect as fees. Defaults to 2**128 - 1.
            amount1Max (int, optional): Maximum amount of token1 to collect as fees. Defaults to 2**128 - 1.
            deadline (int, optional): Unix timestamp after which the transactions will revert. Defaults to 5 minutes from the current block time.

        Returns:
            dict: A summary of the operations performed with transaction hashes for:
                - "decrease_liquidity_tx": Transaction hash for decreasing liquidity.
                - "collect_fees_tx": Transaction hash for collecting fees.
                - "burn_nft_tx": Transaction hash for burning the NFT.

        Raises:
            RuntimeError: If any of the operations fail.
        """
        try:
            self.logger.info(f"Closing liquidity position for Token ID: {self.nft_token_id}...")

            # Step 1: Decrease liquidity
            self.logger.info("Step 1: Decreasing liquidity...")
            decrease_tx_hash = self.decrease_liquidity(amount0Min, amount1Min)

            # Step 2: Collect fees
            self.logger.info("Step 2: Collecting fees...")
            collect_tx_hash = self.collect_fees(amount0Max, amount1Max)

            # Step 3: Burn the NFT
            self.logger.info("Step 3: Burning the NFT...")
            burn_tx_hash = self.burn_nft()

            # Return a summary of the transactions
            result = {
                "decrease_liquidity_tx": decrease_tx_hash,
                "collect_fees_tx": collect_tx_hash,
                "burn_nft_tx": burn_tx_hash,
            }
            self.logger.info(f"Liquidity position closed successfully")
            return result

        except Exception as e:
            self.logger.error(f"Failed to close liquidity position: {e}")
            raise RuntimeError("Failed to close liquidity position.") from e

    def decrease_liquidity(self, amount0Min=0, amount1Min=0):
        """
        Decreases liquidity for the position with the specified parameters.

        This function:
        - Retrieves the current liquidity associated with the position.
        - Sends a transaction to decrease the liquidity.
        - Waits for the transaction to be confirmed.

        Args:
            amount0Min (int, optional): Minimum amount of token0 to receive. Defaults to 0.
            amount1Min (int, optional): Minimum amount of token1 to receive. Defaults to 0.

        Returns:
            str: Transaction hash of the decrease liquidity operation.

        Raises:
            RuntimeError: If decreasing liquidity fails.
        """
        try:
            # Retrieve current liquidity for the position
            position = self.nft_contract.functions.positions(self.nft_token_id).call()
            current_liquidity = position[7]  # Liquidity amount
            self.logger.info(f"Current liquidity for Token ID {self.nft_token_id}: {current_liquidity}")

            # Prepare decrease parameters
            decrease_params = {
                "tokenId": self.nft_token_id,
                "liquidity": current_liquidity,
                "amount0Min": amount0Min,
                "amount1Min": amount1Min,
                "deadline": self.blockchain_connector.web3.eth.get_block("latest")["timestamp"] + 3 * 60,  # Deadline 3 minute from now
            }

            # Build and send the transaction
            self.logger.info(f"Decreasing liquidity for Token ID: {self.nft_token_id}...")
            decrease_function = self.nft_contract.functions.decreaseLiquidity(decrease_params)
            tx_hash, receipt = self.blockchain_connector.build_and_send_transaction(decrease_function)

            self.logger.info(f"Liquidity decreased successfully. Transaction hash: {tx_hash}")
            return tx_hash

        except Exception as e:
            self.logger.error(f"Failed to decrease liquidity: {e}")
            raise RuntimeError("Failed to decrease liquidity.") from e

    def collect_fees(self, amount0Max=2**128 - 1, amount1Max=2**128 - 1):
        """
        Collects trading fees accrued by the liquidity position.

        This function:
        - Prepares and sends a transaction to collect fees.
        - Waits for the transaction to be confirmed.
        - Logs the collected fee amounts.

        Args:
            amount0Max (int, optional): Maximum amount of token0 to collect. Defaults to 2**128 - 1.
            amount1Max (int, optional): Maximum amount of token1 to collect. Defaults to 2**128 - 1.

        Returns:
            str: Transaction hash of the collect fees operation.

        Raises:
            RuntimeError: If collecting fees fails.
        """
        try:
            # Prepare fee collection parameters
            collect_params = {
                "tokenId": self.nft_token_id,
                "recipient": self.blockchain_connector.public_address,
                "amount0Max": amount0Max,
                "amount1Max": amount1Max,
            }

            # Build and send the transaction
            self.logger.info(f"Collecting fees for Token ID: {self.nft_token_id}...")
            collect_function = self.nft_contract.functions.collect(collect_params)
            tx_hash, receipt = self.blockchain_connector.build_and_send_transaction(collect_function)

            self.logger.info(f"Fees collected successfully. Transaction hash: {tx_hash}")
            return tx_hash

        except Exception as e:
            self.logger.error(f"Failed to collect fees: {e}")
            raise RuntimeError("Failed to collect fees.") from e

    def burn_nft(self):
        """
        Burns the NFT associated with the liquidity position.

        This function:
        - Sends a transaction to burn the NFT.
        - Waits for the transaction to be confirmed.
        - Logs the successful burning of the NFT.

        Returns:
            str: Transaction hash of the burn operation.

        Raises:
            RuntimeError: If burning the NFT fails.
        """
        try:
            # Build and send the transaction to burn the NFT
            self.logger.info(f"Burning NFT for Token ID: {self.nft_token_id}...")
            burn_function = self.nft_contract.functions.burn(self.nft_token_id)
            tx_hash, receipt = self.blockchain_connector.build_and_send_transaction(burn_function)

            self.logger.info(f"NFT burned successfully. Transaction hash: {tx_hash}")
            return tx_hash

        except Exception as e:
            self.logger.error(f"Failed to burn NFT: {e}")
            raise RuntimeError("Failed to burn NFT.") from e
