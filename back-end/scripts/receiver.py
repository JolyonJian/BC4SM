import sys
sys.path.append('../utils/')
from eth_instance import *
import json

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

# load smart contract address
def load_contract(eth, path):
    with open("../outputs/" + str(path), 'r') as f:
        contract = json.loads(f.read())
    return eth.contract(contract['address'], contract['abi'])

if __name__ == "__main__":
    eth = EthInstance("127.0.0.1", '8545')

    addr_self = eth.accounts()[0]
    addr_other = eth.accounts()[1]

    contract = load_contract(eth, 'message.json')

    curr_id = contract.functions.getMsgids().call()
    confs = contract.functions.getMessageConf(curr_id).call({'from': addr_self})
    print('[INFO] Get message conf from contract.')
    private_key = RSA.import_key(open('../keys/' + addr_self + '-private.pem').read())
    enc_session_key = confs[0]
    nonce = confs[1]
    tag = confs[2]

    seglength = contract.functions.getCxtLength(curr_id).call({'from': addr_self})
    ciphertext = b''
    seg_size = 20 * 1024
    for i in range(0, seglength, seg_size):
        slice_size = min(seg_size, seglength - i)
        slice = contract.functions.getMessageCxt(curr_id, i, slice_size).call({'from': addr_self})
        ciphertext += slice
    print('[INFO] Get message context from contract.')

    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    print('[INFO] Get data: ')
    print(data.decode("utf-8"))