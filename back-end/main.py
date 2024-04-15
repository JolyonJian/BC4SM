from flask import Flask, request, jsonify
from flask_cors import CORS

from utils.eth_instance import *

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

import json
import bson

import time

app = Flask(__name__)
CORS(app)

eth = EthInstance("127.0.0.1", "8545")

# load smart contract address
def load_contract(eth, path):
    with open("./outputs/" + str(path), 'r') as f:
        contract = json.loads(f.read())
    return eth.contract(contract['address'], contract['abi'])

def generate_id():
    return bson.ObjectId()

def registPubKey(eth, sender, receiver):
    # generate RSA key
    key = RSA.generate(2048)
    private_key = key.export_key()
    path = './keys/' + sender
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

@app.route('/user/listall', methods=['GET'])
def getAllUser():
    contract = load_contract(eth, 'register.json')
    users = contract.functions.getAllUser().call()
    user_info = []
    for user in users:
        user_info.append({'name': user[0], 'addr': user[1]})
    print(user_info)
    return jsonify({'user_list': user_info})

@app.route('/key/register', methods=['POST'])
def registKey():
    sender = request.json.get('sender')
    receiver = request.json.get('receiver')
    start_time = time.time()
    registPubKey(eth, receiver, sender)
    end_time = time.time()
    return jsonify({'result': 200, 'time': (end_time - start_time) * 1000})

@app.route('/file/upload', methods=['POST'])
def uploadFile():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    # 将文件保存到指定目录
    file.save('./uploads/' + file.filename)
    return jsonify({'result': 200})

# 从区块链获取接收方公钥
@app.route('/send/getkey', methods=['POST'])
def getPubKey():
    sender = request.json.get('sender')
    receiver = request.json.get('receiver')
    # get public key
    start_time = time.time()
    contract = load_contract(eth, 'km.json')
    pub_key = contract.functions.getPubKey(receiver).call({'from': sender})
    end_time = time.time()
    print('[INFO] Get the public key.')
    print(pub_key)
    with open("./message/public.pem", "wb") as f:
        f.write(pub_key)
    return jsonify({'result': 200, 'time': (end_time - start_time) * 1000})

@app.route('/send/encrypt', methods=['POST'])
def encryptFile():
    file = request.json.get('file')

    start_time = time.time()
    recipient_key = RSA.import_key(open("./message/public.pem").read())
    session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Read data from dataset
    with open("./data/" + file, "rb") as file:
        data = file.read()

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)
    end_time = time.time()

    with open("./message/encrypted_conf.bin", "wb") as f:
        f.write(cipher_aes.nonce)
        f.write(tag)
        f.write(enc_session_key)

    with open("./message/encrypted_data.bin", "wb") as f:
        f.write(ciphertext)

    return jsonify({'result': 200, 'time': (end_time - start_time) * 1000})

@app.route('/send/blockchain', methods=['POST'])
def sendToBlockchain():
    sender = request.json.get('sender')
    receiver = request.json.get('receiver')

    # Read data from file
    with open("./message/encrypted_conf.bin", "rb") as f:
        nonce = f.read(16)
        tag = f.read(16)
        enc_session_key = f.read()

    with open("./message/encrypted_data.bin", "rb") as f:
        ciphertext = f.read()

    start_time = time.time()
    chunk_size = 100 * 1024  # 100 KB
    # 将字节数据分割成大小为100KB的段
    chunks = [ciphertext[i:i + chunk_size] for i in range(0, len(ciphertext), chunk_size)]
    print('[INFO] The message will be divided into %d segments' % (len(chunks)))

    contract = load_contract(eth, 'message.json')

    print('[INFO] Message send start.')

    eth.minerStart()
    eth.unlockAccount(sender, '123456')

    msg_id = str(generate_id())
    tx_hash = contract.functions.addMessage(msg_id, sender, receiver, enc_session_key, nonce,
                                            tag).transact({'from': sender, 'gas': 999999999})
    tx_receipt = eth.getReceipt(tx_hash)
    print('[INFO] The message has been added.')

    for i in range(len(chunks)):
        tx_hash = contract.functions.addMessageCxt(msg_id, chunks[i]).transact({'from': sender, 'gas': 999999999})
        tx_receipt = eth.getReceipt(tx_hash)
        print('[INFO] Sending the %d/%d segment' % (i + 1, len(chunks)))

    eth.minerStop()
    end_time = time.time()

    print('[INFO] Message send over.')

    return jsonify({'result': 200, 'time': (end_time - start_time) * 1000})

@app.route('/receive/conf', methods=['POST'])
def getRecvkey():
    receiver = request.json.get('receiver')

    start_time = time.time()
    contract = load_contract(eth, 'message.json')

    curr_id = contract.functions.getMsgids().call()
    confs = contract.functions.getMessageConf(curr_id).call({'from': receiver})
    end_time = time.time()
    print('[INFO] Get message conf from contract.')
    with open("./message/msg_conf.bin", "wb") as f:
        f.write(confs[1])
        f.write(confs[2])
        f.write(confs[0])

    return jsonify({'result': 200, 'time': (end_time - start_time) * 1000})

@app.route('/receive/data', methods=['POST'])
def getRecvdata():
    receiver = request.json.get('receiver')

    start_time = time.time()
    contract = load_contract(eth, 'message.json')
    curr_id = contract.functions.getMsgids().call()
    seglength = contract.functions.getCxtLength(curr_id).call({'from': receiver})
    ciphertext = b''
    seg_size = 20 * 1024
    for i in range(0, seglength, seg_size):
        slice_size = min(seg_size, seglength - i)
        slice = contract.functions.getMessageCxt(curr_id, i, slice_size).call({'from': receiver})
        ciphertext += slice
    end_time = time.time()
    with open("./message/msg_data.bin", "wb") as f:
        f.write(ciphertext)
    print('[INFO] Get message context from contract.')

    return jsonify({'result': 200, 'time': (end_time - start_time) * 1000})

@app.route('/receive/decrypt', methods=['POST'])
def getRecvdec():
    receiver = request.json.get('receiver')
    file = request.json.get('file')

    # Read data from file
    private_key = RSA.import_key(open('./keys/' + receiver + '-private.pem').read())
    with open("./message/msg_conf.bin", "rb") as f:
        nonce = f.read(16)
        tag = f.read(16)
        enc_session_key = f.read()

    with open("./message/msg_data.bin", "rb") as f:
        ciphertext = f.read()

    start_time = time.time()
    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    print('[INFO] Get data: ')
    end_time = time.time()

    with open("./results/result." + file.split('.')[-1], "wb") as f:
        f.write(data)

    return jsonify({'result': 200, 'time': (end_time - start_time) * 1000})

if __name__ == "__main__":
    app.run(debug=True, port=3000)