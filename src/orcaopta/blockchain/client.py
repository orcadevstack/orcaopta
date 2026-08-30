from web3 import Web3

class BlockchainClient:
    def __init__(self, rpc):
        self.web3 = Web3(Web3.HTTPProvider(rpc))

    def log(self, message):
        # TODO: call smart contract
        return {"logged": message}

    def verify(self, entry_id):
        return {"verified": entry_id}
