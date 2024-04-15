import sys
sys.path.append('../utils/')
from eth_instance import *
import json
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import bson

def generate_id():
    return bson.ObjectId()

# load smart contract address
def load_contract(eth, path):
    with open("../outputs/" + str(path), 'r') as f:
        contract = json.loads(f.read())
    return eth.contract(contract['address'], contract['abi'])

if __name__ == "__main__":
    eth = EthInstance("127.0.0.1", '8545')

    addr_self = eth.accounts()[1]
    addr_other = eth.accounts()[0]

    # get public key
    contract = load_contract(eth, 'km.json')

    pub_key = contract.functions.getPubKey(addr_other).call({'from': addr_self})
    print('[INFO] Get the public key.')

    recipient_key = RSA.import_key(pub_key)
    session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Read data from dataset
    with open("../data/test.csv", "rb") as file:
        data = file.read()

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)

    chunk_size = 100 * 1024 # 100 KB
    # 将字节数据分割成大小为100KB的段
    chunks = [ciphertext[i:i+chunk_size] for i in range(0, len(ciphertext), chunk_size)]
    print('[INFO] The message will be divided into %d segments' % (len(chunks)))

    contract = load_contract(eth, 'message.json')

    print('[INFO] Message send start.')

    eth.minerStart()
    eth.unlockAccount(addr_self, '123456')

    msg_id = str(generate_id())
    tx_hash = contract.functions.addMessage(msg_id, addr_self, addr_other, enc_session_key, cipher_aes.nonce, tag).transact({'from': addr_self, 'gas': 999999999})
    tx_receipt = eth.getReceipt(tx_hash)
    print('[INFO] The message has been added.')

    for i in range(len(chunks)):
        tx_hash = contract.functions.addMessageCxt(msg_id, chunks[i]).transact({'from': addr_self, 'gas': 999999999})
        tx_receipt = eth.getReceipt(tx_hash)
        print('[INFO] Sending the %d/%d segment' % (i + 1, len(chunks)))

    eth.minerStop()

    print('[INFO] Message send over.')