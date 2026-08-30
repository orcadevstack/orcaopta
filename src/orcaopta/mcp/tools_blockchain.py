from src.orcaopta.blockchain.client import BlockchainClient
import os

bc = BlockchainClient(os.getenv("ORCAOPTA_BLOCKCHAIN_RPC", "http://localhost:8545"))

def tool_blockchain_log(message: str):
    return bc.log(message)

def tool_blockchain_verify(entry_id: str):
    return bc.verify(entry_id)
