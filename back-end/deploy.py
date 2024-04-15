from utils.eth_instance import EthInstance
from hexbytes import HexBytes
import json
import os

class HexJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HexBytes):
            return obj.hex()
        return super().default(obj)

if __name__ == "__main__":
    # create eth interface
    eth = EthInstance("127.0.0.1", "8545")

    # smart contract compilation and deployment
    eth.minerStart()

    for file in os.listdir('./contracts'):
        print('[Info] Loading the contract files: ' + str(file))

        contract_interface = eth.compile('./contracts/' + str(file))
        tx_receipt = eth.deploy(eth.accounts()[0], contract_interface)
        print('[Info] The contract has been deployed successfully at address:', tx_receipt['contractAddress'])

        # save smart contract information
        contract_info = {"name": str(file)[:-4], "address": tx_receipt['contractAddress'], "abi": contract_interface['abi'],
                          "bytecode": contract_interface['bin'],
                          "receipt": json.dumps(dict(tx_receipt), cls=HexJsonEncoder)}

        with open('./outputs/' + str(file)[:-4] + '.json', 'w') as f:
            f.write(json.dumps(contract_info))
        print('[Info] The contract information has been written in ./outputs/' + str(file)[:-4] + '.json')

    eth.minerStop()