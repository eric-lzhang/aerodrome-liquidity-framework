# aerodrome-liquidity-framework
A robust open-source framework for automating liquidity pool position management on Aerodrome Finance, providing essential tools and utilities for efficient DeFi operations.

## Setup Instructions

### Prerequisites
- Python 3.9.7 or higher installed.
- An Infura API key (for connecting to the Base network).
    - You can get it for free from https://www.infura.io/
    - OR, you can get an Alchemy API key from https://www.alchemy.com/
- A valid Ethereum private key.

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
PROVIDER=INFURA or ALCHEMY
INFURA_PROJECT_ID=the project id from Infura
ALCHEMY_PROJECT_ID=optional, the api from Alchemy
PRIVATE_KEY=eth private key

Example `.env`:
PROVIDER=INFURA
INFURA_PROJECT_ID=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
ALCHEMY_PROJECT_ID=sQlw3r8hJbPclaDBH4eabydo5pf-YJAl
PRIVATE_KEY=afdfd9c3dc095ef696594f6cedcae52e72dcd697e2a952115781444224f89

### 5. Make A Demo Run

Run main.py to get your wallet balance:

```bash
python main.py
```