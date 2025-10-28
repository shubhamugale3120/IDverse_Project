import os, json
from web3 import Web3

w3 = Web3(Web3.HTTPProvider(os.environ.get("WEB3_PROVIDER", "http://127.0.0.1:8545")))
cred_addr = os.environ.get("CREDENTIAL_REGISTRY_ADDRESS")
cred_abi_path = os.environ.get("CREDENTIAL_REGISTRY_ABI")

def load_contract():
    if not cred_addr or not cred_abi_path:
        return None
    abi = json.load(open(cred_abi_path))["abi"]
    return w3.eth.contract(address=cred_addr, abi=abi)

def issue_on_chain(private_key, holder_addr, vcType_bytes32, cid_hash_bytes32, expiresAt):
    cred = load_contract()
    acct = w3.eth.account.from_key(private_key)
    tx = cred.functions.issue(holder_addr, vcType_bytes32, cid_hash_bytes32, expiresAt).buildTransaction({
        "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address), "gas": 500000
    })
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt
