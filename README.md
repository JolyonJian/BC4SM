# BC4SM: Blockchain-based secure messaging

---

### 项目说明
本项目是一个基于区块链的安全数据传输工具，基于以太坊区块链平台实现混合密钥方案，用于在两个用户间传输文件。

技术架构：

- 前端： Vue3 + TypeScript + element Plus
- 后端： Python + Flask + Web3.py
- 区块链：以太坊 + Solidity

作为一个demo，可以传递财务、电气等不同行业的数据，利用区块链赋能各个领域。

### 目录说明

```
/blockchian
	/contracts: 存放系统使用的智能合约
		/km.sol: 密钥管理
		/message.sol: 消息传输
		/register.sol: 用户注册
	/data: 存放测试数据
	/keys: 存放用户生成的密钥文件
	/message: 存放通信过程中生成的中间文件
	/outputs: 存放编译后的智能合约
	/results: 存放消息传输的最终结果
	/scripts: 不运行前端界面时，可以通过该目录下的脚本实现传输
	/uploads: 存放前端上传的文件
	/utils: 封装的以太坊交互接口
	/deploy.py: 部署智能合约
	/init.py: 初始化用户
	/main.py: flask应用入口
/back-end
	/conf: 区块链配置信息
	/data: 存放区块链数据
	/geth.exe: 以太坊客户端
	/init.bat: 初始化脚本
	/run.bat: 运行脚本
/front-end
	/bc4sm: 前端vue项目

```
### 环境说明
开发使用的环境版本如下：

- 区块链： geth(v1.11.6) solc(0.7.0)
- 后端：python(3.11.7)
- 前端：nodejs(v16.20.2)
- 数据集：[Individual Household Electric Power Consumption](https://archive.ics.uci.edu/dataset/235/individual%20household%20electric%20power%20consumption)
- OS: Windows 11


### 运行说明
1. 克隆本仓库
```
git clone https://github.com/JolyonJian/BC4SM
cd BC4SM
```
2. 启动区块链客户端
```
cd BC4SM/blockchain
./init.sh # 仅首次运行及清空区块链数据重新启动时需要
./run.sh 
```
init脚本默认创建两个用户，启动geth console后，需要在geth命令行中运行如下命令，为用户准备以太币进行后续操作：
```
miner.setEtherbase(eth.accounts[0])
miner.start()
miner.stop()
miner.setEtherbase(eth.accounts[1])
miner.start()
miner.stop()
```
3. 启动后端
```
cd BC4SM/back-end
pip install -r requirement.txt
python deploy.py
python init.py
# 1. 如果需要运行后端flask应用响应前端请求，则运行：
python main.py
# 2. 如果无需运行前端前面，可以直接：
cd scripts
python registPubKey.py
python sender.py
python receiver.py
```
4. 启动前端
```
cd BCSM/front-end/bc4sm/
npm install
npm run serve
```

### 运行演示

![运行演示](https://s1.locimg.com/2024/04/15/4637b3d033042.gif)

