import os
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

load_dotenv()

RPC_URL = "https://evmrpc-testnet.0g.ai"
CHAIN_ID = 16602

AGENT_REGISTRY_ADDRESS = "0x2CadF05349225422AA92087B5BFDCf094c632443"
MARKETPLACE_ADDRESS = "0x11bc34d3C4C2C0f549B61bfB101D056e599bF9Fa"


class ContractUtils:
    def __init__(self):
        self.private_key = os.getenv("PRIVATE_KEY")
        if not self.private_key:
            raise ValueError("❌ PRIVATE_KEY not found in .env")

        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        self.account = Account.from_key(self.private_key)

    def get_registry_contract(self):
        abi = [
            {"inputs": [{"internalType": "string", "name": "name", "type": "string"},
                        {"internalType": "string", "name": "description", "type": "string"}], "name": "registerAgent",
             "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "nonpayable",
             "type": "function"},
            {"inputs": [{"internalType": "address", "name": "owner", "type": "address"}], "name": "getAgentId",
             "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view",
             "type": "function"},
            {"inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "name": "agentName",
             "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view",
             "type": "function"},
            {"inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "name": "agentDescription",
             "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view",
             "type": "function"}
        ]
        return self.w3.eth.contract(address=AGENT_REGISTRY_ADDRESS, abi=abi)

    def get_marketplace_contract(self):
        abi = [
            {"inputs": [{"internalType": "uint256", "name": "agentId", "type": "uint256"},
                        {"internalType": "string", "name": "description", "type": "string"},
                        {"internalType": "uint256", "name": "reward", "type": "uint256"}], "name": "createTask",
             "outputs": [], "stateMutability": "payable", "type": "function"},
            {"inputs": [{"internalType": "uint256", "name": "taskId", "type": "uint256"}], "name": "completeTask",
             "outputs": [], "stateMutability": "nonpayable", "type": "function"},
            {"inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "name": "tasks", "outputs": [
                {"internalType": "uint256", "name": "taskId", "type": "uint256"},
                {"internalType": "address", "name": "requester", "type": "address"},
                {"internalType": "uint256", "name": "agentId", "type": "uint256"},
                {"internalType": "string", "name": "description", "type": "string"},
                {"internalType": "uint256", "name": "reward", "type": "uint256"},
                {"internalType": "bool", "name": "completed", "type": "bool"},
                {"internalType": "bool", "name": "exists", "type": "bool"}
            ], "stateMutability": "view", "type": "function"}
        ]
        return self.w3.eth.contract(address=MARKETPLACE_ADDRESS, abi=abi)

    def send_transaction(self, function):
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

    def send_transaction_with_value(self, function, value_wei: int):
        tx = function.build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 800000,
            'gasPrice': self.w3.eth.gas_price,
            'chainId': CHAIN_ID,
            'value': value_wei
        })
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt, tx_hash.hex()

    def get_all_registered_agents(self):
        try:
            registry = self.get_registry_contract()
            next_id = registry.functions.nextAgentId().call()

            agents = []
            for agent_id in range(1, next_id):
                try:
                    name = registry.functions.agentName(agent_id).call()
                    description = registry.functions.agentDescription(agent_id).call()
                    agents.append({
                        "id": agent_id,
                        "name": name,
                        "description": description if description else "No description provided",
                        "owner": "0x..."
                    })
                except:
                    continue
            return agents
        except Exception as e:
            print(f"Error fetching agents: {e}")
            return []

    def get_my_tasks(self):
        """Safe method to fetch user's tasks"""
        try:
            marketplace = self.get_marketplace_contract()
            my_tasks = []

            for task_id in range(1, 50):  # Scan reasonable range
                try:
                    task = marketplace.functions.getTask(task_id).call()
                    if task[6] == True and task[1] == self.account.address:  # exists and requester is me
                        my_tasks.append({
                            "id": task[0],
                            "agentId": task[2],
                            "description": task[3],
                            "reward": task[4],
                            "completed": task[5]
                        })
                except:
                    continue
            return my_tasks
        except Exception as e:
            print(f"Error fetching my tasks: {e}")
            return []