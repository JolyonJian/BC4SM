# BC4SM: Blockchain-based secure messaging

---

### Project Overview

This project is a secure data transmission tool based on blockchain, implemented on the Ethereum blockchain platform using a hybrid key scheme, designed for transferring files between two users.

Technical Stack:

- Frontend:  `Vue3 + TypeScript + element Plus`
- Backend:  `Python + Flask + Web3.py`
- Blockchain:  `Ethereum + Solidity`

As a demo, it can be used to transmit data from various industries such as finance and electricity, leveraging blockchain to empower different sectors.

### Directory Structure

```
/blockchian
	/contracts: Contains the smart contracts used by the system
		/km.sol: Key management
		/message.sol: Message transmission
		/register.sol: User registration
	/data: Stores test data
	/keys: Stores user-generated key files
	/message: Stores intermediate files generated during communication
	/outputs: Stores compiled smart contracts
	/results: Stores the final results of message transmission
	/scripts: When not running the frontend interface, transmission can be achieved through scripts in this directory
	/uploads: Stores files uploaded by the frontend
	/utils: Encapsulated Ethereum interaction interfaces
	/deploy.py: Deploys smart contracts
	/init.py: Initializes users
	/main.py: Entry point for Flask application
/back-end
	/conf: Blockchain configuration information
	/data: Stores blockchain data
	/geth.exe: Ethereum client
	/init.bat: Initialization script
	/run.bat: Run script
/front-end
	/bc4sm: Frontend Vue project
```

### Environment Setup

Versions of the environment used in development are as follows:

- Blockchain: geth(v1.11.6), solc(0.7.0)
- Backend: Python(3.11.7)
- Frontend: Node.js(v16.20.2)
- Dataset: [Individual Household Electric Power Consumption](https://archive.ics.uci.edu/dataset/235/individual%20household%20electric%20power%20consumption)
- OS: Windows 11

### Running Instructions

1. Clone this repository

```
git clone https://github.com/JolyonJian/BC4SM
cd BC4SM
```
2. Start the blockchain client

```
cd BC4SM/blockchain
./init.sh # Only required for the first run and when restarting to clear blockchain data
./run.sh 
```
The init script by default creates two users. After starting the geth console, run the following commands in the geth command line to prepare ether for the users for subsequent operations:

```
miner.setEtherbase(eth.accounts[0])
miner.start()
miner.stop()
miner.setEtherbase(eth.accounts[1])
miner.start()
miner.stop()
```
3. Start the backend

```
cd BC4SM/back-end
pip install -r requirement.txt
python deploy.py
python init.py
# 1. If you need to run the backend Flask application to respond to frontend requests, run:
python main.py
# 2. If frontend is not needed, you can directly run:
cd scripts
python registPubKey.py
python sender.py
python receiver.py
```
4. Start the frontend
```
cd BCSM/front-end/bc4sm/
npm install
npm run serve
```

### Demo

![demo](https://s1.locimg.com/2024/04/15/4637b3d033042.gif)