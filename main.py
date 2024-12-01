# main.py

import time
import logging
from logging_config import setup_logging
from utils.blockchain_connector import BlockchainConnector
from utils.liquidity_manager import LiquidityManager

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)
logger.info("-------------------- Initialize Aerodrome Liquidity Framework --------------------")

def main():
    # In your terminal, run "python3 main.py" to show this demo
    # If the program terminates unexpectedly, you can enable the detailed logging to help you debug.
    # To enble, go to the __init__ in blockchain_connector.py and liquidity_manager.py.
    # Comment out the "self.logger.disabled = True" line

    # Run this function when you added:
    # PROVIDER, INFURA_PROJECT_ID, and PRIVATE_KEY
    demo_blockchain_connector()
    
    # Comment out the line after the next line and run the function when you have the following crypto in your wallet:
    # 3 USDC, 0.001 WETH, 0.001 ETH
    # demo_liquidity_manager()

def demo_blockchain_connector():
    # Initialize Blockchain Connector
    logger.info("\n")
    logger.info("-------------------------------------------------------------------------")
    logger.info("------------------------- Connect to Blockchain -------------------------")
    logger.info("-------------------------------------------------------------------------")
    logger.info("Connecting to Blockchain...")
    try:
        blockchain_connector = BlockchainConnector()
    except Exception as e:
        logger.error(f"Error connecting to the blockchain: {e}")
        logger.error(f"Please check the READEME to ensure you have:")
        logger.error(f"1. Created and Activated Virtual Environment")
        logger.error(f"2. Installed Dependencies")
        logger.error(f"3. Added Environment Variables")
        raise
    logger.info("Blockchain is connected")

    wallet_address = blockchain_connector.public_address
    
    logger.info("\n")
    logger.info("-------------------------------------------------------------------------")
    logger.info("--------------------------- Wallet Information --------------------------")
    logger.info("-------------------------------------------------------------------------")

    eth_balance = blockchain_connector.get_balance()
    if eth_balance is not None:
        logger.info(f"The ETH wallet balance for your wallet {wallet_address} is: {eth_balance}")
    else:
        logger.error(f"Failed to retrieve the wallet balance for {wallet_address}")

    weth_balance = blockchain_connector.get_token_balance(blockchain_connector.token_addresses["WETH"])
    if weth_balance is not None:
        logger.info(f"The WETH wallet balance for your wallet {wallet_address} is: {weth_balance}")
    else:
        logger.error(f"Failed to retrieve the wallet balance for {wallet_address}")

    usdc_balance = blockchain_connector.get_token_balance(blockchain_connector.token_addresses["USDC"])
    if usdc_balance is not None:
        logger.info(f"The USDC wallet balance for your wallet {wallet_address} is: {usdc_balance}")
    else:
        logger.error(f"Failed to retrieve the wallet balance for {wallet_address}")

def demo_liquidity_manager():
    # Set up pool parameters
    pool_name="CL100_WETH_USDC"
    weth_amount=0.001  # Example: you will put a maximum of 0.001 WETH into the liquidity pool
    usdc_amount=3.0  # Example: you will put a maximum of 3 USDC into the liquidity pool
    lower_range_percentage=3  # Example: 3% lower range. Specify the lower price range where the liquidity position will be active.
    upper_range_percentage=3  # Example: 3% upper range. Specify the upper price range where the liquidity position will be active.

    # Other setups
    eth_amount=0.001 # Example: make sure your have enough eth to cover the gas fee. 0.001 ETH is usually enough for a demo.
    pause_time=3 * 60 # Example: the program will pause for 3 minutes after opening and before closing the position pool.

    # In this example, if the current price for ETH-USDC is 3000 USDC per ETH,
    # then the liquidity position will be active for roughly 3000 * (1 - 0.035) = 2895 and 3000 * (1 + 0.035) = 3105.
    # To get the more accurate price range calculation, please refer to the LiquidityManager.get_pool_status() method.

    liquidity_manager = LiquidityManager(
        pool_name=pool_name,
        token0_max=weth_amount,
        token1_max=usdc_amount,
        lower_range_percentage=lower_range_percentage,
        upper_range_percentage=upper_range_percentage
    )

    logger.info("\n")
    logger.info("-------------------------------------------------------------------------")
    logger.info("-------------------- Liquidity Position Target Setup --------------------")
    logger.info("-------------------------------------------------------------------------")
    logger.info(f"You will open a liquidity position for the {pool_name} pool")
    logger.info(f"You will invest at most {weth_amount} WETH into this position")
    logger.info(f"You will invest at most {usdc_amount} USDC into this position")

    logger.info("\n")
    logger.info("-------------------------------------------------------------------------")
    logger.info("------------------------ Ensure Sufficient Token ------------------------")
    logger.info("-------------------------------------------------------------------------")
    blockchain_connector = BlockchainConnector()
    eth_balance = blockchain_connector.get_balance()
    weth_balance = blockchain_connector.get_token_balance(blockchain_connector.token_addresses["WETH"])
    usdc_balance = blockchain_connector.get_token_balance(blockchain_connector.token_addresses["USDC"])
    if eth_balance is None or eth_balance < eth_amount:
        logger.error(f"Insufficient ETH amount: You have {eth_balance}. You need {eth_amount} to proceed.")
        raise Exception("Please provide sufficient amount of token to proceed.")
    if weth_balance is None or weth_balance < weth_amount:
        logger.error(f"Insufficient WETH amount: You have {weth_balance}. You need {weth_amount} to proceed.")
        raise Exception("Please provide sufficient amount of token to proceed.")
    if usdc_balance is None or usdc_balance < usdc_amount:
        logger.error(f"Insufficient USDC amount: You have {usdc_balance}. You need {usdc_amount} to proceed.")
        raise Exception("Please provide sufficient amount of token to proceed.")
    logger.info(f"You have sufficient token in ETH, WETH, and USDC")

    # Open the liquidity position using the above parameter
    logger.info("\n")
    logger.info("-------------------------------------------------------------------------")
    logger.info("------------------------ Open Liquidity Position ------------------------")
    logger.info("-------------------------------------------------------------------------")
    logger.info(f"Opening the liquidity position...")
    liquidity_manager.open_liquidity_position()
    logger.info(f"Liquidity position opened")

    logger.info(f"The WETH price when you started this liquidity position is: {liquidity_manager.start_pool_status['current_price']}")
    logger.info(f"the WETH price range (in USDC) within which the liquidity position will be active is between:")
    logger.info(f"{liquidity_manager.start_pool_status['lower_price']} and {liquidity_manager.start_pool_status['upper_price']}")
    logger.info(f"You invested {liquidity_manager.amount0} WETH")
    logger.info(f"You invested {liquidity_manager.amount1} USDC")
    logger.info(f"The NFT token id that represents your ownership of this position is {liquidity_manager.nft_token_id}")

    # Pause for 3 minutes. You can verify your position by going to https://aerodrome.finance/dash and connecting your wallet to aerodrome finance.
    logger.info("\n")
    logger.info("-------------------------------------------------------------------------")
    logger.info("--------------------------- Check It Yourself ---------------------------")
    logger.info("-------------------------------------------------------------------------")
    logger.info(f"Pausing for 3 minutes")
    logger.info(f"You can verify your position by going to https://aerodrome.finance/dash and connecting your wallet to aerodrome finance")
    time.sleep(pause_time)

    # Close the liquidity position using the above parameter
    logger.info("\n")
    logger.info("-------------------------------------------------------------------------")
    logger.info("------------------------ Close Liquidity Position -----------------------")
    logger.info("-------------------------------------------------------------------------")
    logger.info(f"Closing the liquidity position...")
    liquidity_manager.close_liquidity_position()
    logger.info(f"Liquidity position closed")

    # Run the demo_blockchain_connector() again to check the balance change in your wallet
    # Note that by maintaining the liquidity position for three minutes, your balance probably will decrease a little.
    demo_blockchain_connector()

if __name__ == "__main__":
    main()
