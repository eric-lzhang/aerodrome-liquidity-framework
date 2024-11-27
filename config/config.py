import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Infura Project ID. Get this from https://www.infura.io/
INFURA_PROJECT_ID = os.getenv('INFURA_PROJECT_ID')

# Alchemy Project ID. Get this from https://www.alchemy.com/
ALCHEMY_PROJECT_ID = os.getenv('ALCHEMY_PROJECT_ID')