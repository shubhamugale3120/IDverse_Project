import os
import ipfshttpclient

IPFS_API = os.environ.get("IPFS_API", "/dns/localhost/tcp/5001/http")

def upload_bytes(data_bytes):
    client = ipfshttpclient.connect(IPFS_API)
    cid = client.add_bytes(data_bytes)
    return cid  # returns CID string

def upload_file(path):
    client = ipfshttpclient.connect(IPFS_API)
    res = client.add(path)
    return res['Hash']

def cat(cid):
    client = ipfshttpclient.connect(IPFS_API)
    return client.cat(cid)
