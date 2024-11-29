import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Private key for deriving the public address
PRIVATE_KEY = os.getenv('PRIVATE_KEY')

# By default, we will use Infura as our web3 provider
PROVIDER = os.getenv('PROVIDER', 'INFURA')  # Default to INFURA

# Infura Project ID. Get this from https://www.infura.io/
INFURA_PROJECT_ID = os.getenv('INFURA_PROJECT_ID')

# Alchemy Project ID. Get this from https://www.alchemy.com/
ALCHEMY_PROJECT_ID = os.getenv('ALCHEMY_PROJECT_ID')

# Maximum Gas Allowed
GAS_AMOUNT = 1000000