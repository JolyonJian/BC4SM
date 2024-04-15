import sys
sys.path.append('../utils/')
from eth_instance import *
from Crypto.PublicKey import RSA
import json

# load smart contract address
def load_contract(eth, path):
    with open("../outputs/" + str(path), 'r') as f:
        contract = json.loads(f.read())
    return eth.contract(contract['address'], contract['abi'])

def registPubKey(eth, sender, receiver):
    # generate RSA key
    key = RSA.generate(2048)
    private_key = key.export_key()
    path = '../keys/' + sender
    with open(path + '-private.pem', 'wb') as f:
        f.write(private_key)

    public_key = key.publickey().export_key()
    with open(path + '-public.pem', 'wb') as f:
        f.write(public_key)

    print('[INFO] Keys has been generated.')

    contract = load_contract(eth, 'km.json')

    eth.minerStart()
    eth.unlockAccount(sender, '123456')
    eth.unlockAccount(receiver, '123456')

    tx_hash = contract.functions.setPubKey(sender, public_key).transact({'from': sender})
    tx_receipt = eth.getReceipt(tx_hash)
    print('[INFO] The public key of sender has been registed.')

    tx_hash = contract.functions.setAuthorization(sender, receiver, 'add').transact({'from': sender})
    tx_receipt = eth.getReceipt(tx_hash)
    print('[INFO] The authorization of receiver has been added.')

    eth.minerStop()


if __name__ == "__main__":
    eth = EthInstance("127.0.0.1", '8545')
    # regist the public key
    sender = eth.accounts()[0]
    receiver = eth.accounts()[1]

    registPubKey(eth, sender, receiver)
    registPubKey(eth, receiver, sender)