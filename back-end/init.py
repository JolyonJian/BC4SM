from utils.eth_instance import *
import json
import random

# 定义名字部分
first_names = ["John", "Alice", "Bob", "Emily", "David", "Emma", "Michael", "Olivia", "James", "Sophia", "Daniel", "Ava", "William", "Mia", "Matthew", "Charlotte", "Joseph", "Amelia", "Andrew", "Ella"]
last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson"]

# 生成随机名字
def generate_random_name():
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    return f"{first_name} {last_name}"

# load smart contract address
def load_contract(eth, path):
    with open("./outputs/" + str(path), 'r') as f:
        contract = json.loads(f.read())
    return eth.contract(contract['address'], contract['abi'])


if __name__ == "__main__":
    eth = EthInstance("127.0.0.1", '8545')


    contract = load_contract(eth, 'register.json')

    # register users
    for account in eth.accounts():
        eth.minerStart()
        eth.unlockAccount(account, '123456')
        tx_hash = contract.functions.addUser(generate_random_name(), account).transact({'from': account})
        tx_receipt = eth.getReceipt(tx_hash)
        print('[INFO] User ', account, ' has been registed.')
        eth.minerStop()

    print('All users: ', contract.functions.getAllUser().call())