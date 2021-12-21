from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()


# compile solidity

install_solc("0.6.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# for connecing to rinkeby
w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/5b881af8ebcc46f18dd698a0e50bf37d")
)
chain_id = 4
my_address = "0x2C43fB4082C4884C213c993b6adCabd8b19B558f"
private_key = os.getenv("PRIVATE_KEY")

print(f"address     : {my_address}")
print(f"private key : {private_key}")

# Create the contract in Python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get the latest transaction count
nonce = w3.eth.getTransactionCount(my_address)
print(f"nonce       : {nonce}\n")

# 1. Build a transaction
# 2. Sign a transaction
# 3. Send a transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {
        # "chainID": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# send the signed transaction
print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Contract Deployed")


# working with contract (Need contract address and ABI)
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Call -> Simulate making the call and getting a return value (doesn't change the blockchain)
# Transact -> Make state change to the blockchain

print(simple_storage.functions.retrieve().call())  # initial value of favouriteNumber
print("Updating contract...")

store_transaction = simple_storage.functions.store(
    15
).buildTransaction(  # create transaction
    {
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
signed_store_txn = w3.eth.account.sign_transaction(  # signing transaction
    store_transaction, private_key=private_key
)
send_store_tx = w3.eth.send_raw_transaction(  # send transaction
    signed_store_txn.rawTransaction
)
tx_receipt = w3.eth.waitForTransactionReceipt(  # wait for transaction to finish
    send_store_tx
)
print("Contract updated")

print(simple_storage.functions.retrieve().call())
