import os
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

# load_dotenv()

RPC_URL = "https://evmrpc-testnet.0g.ai"
CHAIN_ID = 16602

# Your deployed SovereignAgent contract
SOVEREIGN_AGENT_ADDRESS = "0x55072806A808Ad2FA4972136d06388058Ce5156E"


class ContractUtils:
    def __init__(self):
        self.private_key = os.getenv("PRIVATE_KEY")
        if not self.private_key:
            raise ValueError("❌ PRIVATE_KEY not found in .env file")

        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        self.account = Account.from_key(self.private_key)

    def get_agent_contract(self):
        """Returns the SovereignAgent contract"""
        abi = [
            {"inputs": [{"internalType": "string", "name": "name", "type": "string"},
                        {"internalType": "string", "name": "description", "type": "string"}], "name": "createAgent",
             "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "nonpayable",
             "type": "function"},
            {"inputs": [{"internalType": "uint256", "name": "agentId", "type": "uint256"}], "name": "getAgent",
             "outputs": [
                 {"internalType": "address", "name": "owner", "type": "address"},
                 {"internalType": "string", "name": "name", "type": "string"},
                 {"internalType": "string", "name": "description", "type": "string"},
                 {"internalType": "uint256", "name": "createdAt", "type": "uint256"},
                 {"internalType": "bool", "name": "active", "type": "bool"}
             ], "stateMutability": "view", "type": "function"}
        ]
        return self.w3.eth.contract(address=SOVEREIGN_AGENT_ADDRESS, abi=abi)

    def send_transaction(self, function):
        """Send a transaction to the blockchain"""
        tx = function.build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 800000,
            'gasPrice': self.w3.eth.gas_price,
            'chainId': CHAIN_ID
        })
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt, tx_hash.hex()

    def get_agent_id(self, owner_address=None):
        """Get agent ID for an address"""
        if owner_address is None:
            owner_address = self.account.address
        try:
            contract = self.get_agent_contract()
            return contract.functions.getAgentId(owner_address).call() if hasattr(contract.functions,
                                                                                  'getAgentId') else 0
        except:
            return 0
