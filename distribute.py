from web3 import Web3
import yaml
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/distribute.log'),  # 保留文件日志
        logging.StreamHandler()  # 新增控制台输出
    ]
)

# 加载配置文件
with open('config.yaml') as f:
    data = yaml.safe_load(f)

rpc_url = data['network']['rpc_url']

# 提取主地址和私钥
main_address = data['accounts']['main']['address']
private_key = data['accounts']['main']['private_key']
# 提取其他地址
recipient_addresses = [recipient['address'] for recipient in data['accounts']['recipients']]
distribute_amount = data['distribute_amount']
contract_address = data['contractAddress']

# 连接到RPC节点
w3 = Web3(Web3.HTTPProvider(rpc_url))

# 合约编译结果
contract_abi = [
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "depositor",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "Deposited",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "recipient",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "TransferFailure",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "recipient",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "TransferSuccess",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "depositor",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "Withdrawn",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "deposit",
		"outputs": [],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "deposits",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "depositor",
				"type": "address"
			},
			{
				"internalType": "address[]",
				"name": "recipients",
				"type": "address[]"
			},
			{
				"internalType": "uint256",
				"name": "amountPerRecipient",
				"type": "uint256"
			}
		],
		"name": "distributeFixed",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "depositor",
				"type": "address"
			}
		],
		"name": "emergencyWithdraw",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address payable",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "withdraw",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]

def distribute_via_contract(contract_address):
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)
    # 准备参数
    recipients = recipient_addresses
    amount_per_wallet = w3.to_wei(distribute_amount
                                  , 'ether')
    total_needed = amount_per_wallet * len(recipients)

    # 调用deposit函数存款
    deposit_tx = contract.functions.deposit().build_transaction({
        'from': main_address,
        'value': total_needed,
        'gas': 152009,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(main_address),
    })

    signed_deposit = w3.eth.account.sign_transaction(deposit_tx, private_key)
    deposit_hash = w3.eth.send_raw_transaction(signed_deposit.raw_transaction)
    deposit_receipt = w3.eth.wait_for_transaction_receipt(deposit_hash)
    logging.info(f"存款成功，交易哈希: 0x{deposit_hash.hex()}")

    explorer_url = f"https://testnet.monadexplorer.com/tx/0x{deposit_hash.hex()}"
    logging.info(f"区块浏览器链接: {explorer_url}")

    # 分发操作
    distribute_tx = contract.functions.distributeFixed(
        main_address,
        recipients,
        amount_per_wallet
    ).build_transaction({
        'from': main_address,
        'gas': 1000000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(main_address),
    })

    signed_distribute = w3.eth.account.sign_transaction(distribute_tx, private_key)
    distribute_hash = w3.eth.send_raw_transaction(signed_distribute.raw_transaction)
    distribute_receipt = w3.eth.wait_for_transaction_receipt(distribute_hash)
    logging.info(f"分发成功，交易哈希: 0x{distribute_hash.hex()}")
    explorer_url = f"https://testnet.monadexplorer.com/tx/0x{distribute_hash.hex()}"
    logging.info(f"区块浏览器链接: {explorer_url}")
def show_balances():
    main_balance = w3.eth.get_balance(main_address)
    logging.info(f"主地址:{main_address} : {w3.from_wei(main_balance, 'ether')} MON")
    for wallet in recipient_addresses:
        balance = w3.eth.get_balance(wallet)
        logging.info(f"{wallet} : {w3.from_wei(balance, 'ether')} MON")


# 使用示例
if __name__ == "__main__":
    try:
        distribute_via_contract(contract_address)
        show_balances()
    except Exception as e:
        logging.error(f"发生错误: {e}")
