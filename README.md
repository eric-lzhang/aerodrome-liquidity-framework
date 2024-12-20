# Aerodrome Liquidity Framework
A robust open-source framework for automating liquidity pool position management on Aerodrome Finance, providing essential tools and utilities for efficient DeFi operations.

## Setup Instructions

### Prerequisites
- Python 3.9.7 or higher installed.
- An Infura API key (for connecting to the Base network). You can get it for free from [Infura](https://www.infura.io/).
- Alternatively, you can get an Alchemy API key from [Alchemy](https://www.alchemy.com/).
- A valid Ethereum (Base) private key. You can get this by creating a wallet in [Metamask](https://chromewebstore.google.com/detail/metamask/nkbihfbeogaeaoehlefnkodbefgpgknn?hl=en)
- To run the demo of opening and closing a liquidity position, add 0.001 ETH, 0.001 WETH, and 3 USDC in your wallet.

### 1. Clone the Repository

Start by cloning the `aerodrome-liquidity-framework` repository to your local machine using HTTPS:

```bash
git clone https://github.com/eric-lzhang/aerodrome-liquidity-framework.git
cd aerodrome-liquidity-framework
```

### 2. Create and Activate Virtual Environment

Set up a virtual environment to manage project dependencies.

Create Virtual Environment:

```bash
python -m venv venv
```

Activate Virtual Environment:

- macOS/Linux:
    ```bash
    source venv/bin/activate
    ```
- Windows:
    ```bash
    venv\Scripts\activate
    ```        

To Deactivate Virtual Environment:

```bash
deactivate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Add Environment Variables

Create a ".env" file, with the following information:

```env
PROVIDER=INFURA or ALCHEMY
INFURA_PROJECT_ID=the project id from Infura
ALCHEMY_PROJECT_ID=optional, the api from Alchemy
PRIVATE_KEY=eth private key
```

Example `.env`:
```env
PROVIDER=INFURA
INFURA_PROJECT_ID=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
PRIVATE_KEY=afdfd9c3dc095ef696594f6cedcae52e72dcd697e2a952115781444224f89
```

### 5. Run the Test

Run the tests to esure the methods works.
```bash
python -m unittest discover tests
```

### 6. Make A Demo Run - Get Wallet Balance

Run main.py to get your wallet balance:

```bash
python main.py
```

### 7. Add Crypto to Your Wallet

Add 0.001 ETH, 0.001 WETH, and 3 USDC in your wallet correspond to your private key.

### 8. Make A Demo Run - Open and Close a Liquidity Positinon

Uncomment the following line in main.py:

```python
# demo_liquidity_manager()
```

Then, run main.py again to see the life cycle of a liquidity position.
```bash
python main.py
```
