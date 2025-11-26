"""
Mock + factory contract service for demo mode.

- Uses in-memory (optional persisted) store to simulate on-chain issuance/revoke/status.
- Factory returns MockContractService when CHAIN_MODE != "real".
- Keep RealContractService placeholder for later wiring to web3.py.
"""
import os
import time
import uuid
import json
from typing import Dict, Any, Optional

STORE_PATH = os.getenv("MOCK_CONTRACT_STORE", os.path.join("backend", "var", "mock_contract_store.json"))
os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)

class MockContractService:
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        try:
            if os.path.exists(STORE_PATH):
                with open(STORE_PATH, "r", encoding="utf-8") as fh:
                    self._store = json.load(fh)
        except Exception:
            self._store = {}

    def _save(self):
        try:
            with open(STORE_PATH, "w", encoding="utf-8") as fh:
                json.dump(self._store, fh, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _make_vc_id(self) -> str:
        # stable string id (timestamp + uuid)
        return f"{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"

    def issue(self, holder: str, vc_type: str, cid_hash: str, expires_at: Optional[int] = None) -> Dict[str, Any]:
        """
        Simulate issuing a VC on-chain. Returns dict with vcId, txHash, blockNumber.
        """
        vc_id = self._make_vc_id()
        tx_hash = "0x" + uuid.uuid4().hex[:64]
        block_number = 1000 + (int(time.time()) % 1000)
        rec = {
            "vcId": vc_id,
            "holder": holder,
            "vc_type": vc_type,
            "cid_hash": cid_hash,
            "issuedAt": int(time.time()),
            "expiresAt": expires_at,
            "revoked": False,
            "txHash": tx_hash,
            "blockNumber": block_number
        }
        self._store[str(vc_id)] = rec
        self._save()
        return {"vcId": vc_id, "txHash": tx_hash, "blockNumber": block_number}

    def revoke(self, vc_id: str, reason: int = 0) -> Dict[str, Any]:
        """
        Mark vcId as revoked. Raises KeyError if not found.
        """
        key = str(vc_id)
        if key not in self._store:
            raise KeyError("vcId not found")
        self._store[key]["revoked"] = True
        self._store[key]["revokedAt"] = int(time.time())
        self._store[key]["revocationReason"] = int(reason)
        tx_hash = "0x" + uuid.uuid4().hex[:64]
        self._save()
        return {"vcId": vc_id, "txHash": tx_hash}

    def status(self, vc_id: str) -> Dict[str, Any]:
        """
        Return status object for vcId.
        """
        key = str(vc_id)
        rec = self._store.get(key)
        if not rec:
            return {"vcId": vc_id, "found": False, "revoked": False}
        return {
            "vcId": vc_id,
            "found": True,
            "revoked": bool(rec.get("revoked", False)),
            "txHash": rec.get("txHash"),
            "blockNumber": rec.get("blockNumber"),
            "issuedAt": rec.get("issuedAt"),
            "expiresAt": rec.get("expiresAt"),
            "holder": rec.get("holder"),
            "vc_type": rec.get("vc_type"),
            "cid_hash": rec.get("cid_hash")
        }

    def list_all(self) -> Dict[str, Dict[str, Any]]:
        """Return all stored records (for admin/debug)."""
        return self._store

# Placeholder for real contract integration
class RealContractService:
    def __init__(self, rpc_url: str, private_key: str, abi_path: Optional[str] = None, contract_address: Optional[str] = None):
        """
        Implement real web3.py integration here when CHAIN_MODE=real.
        Keep constructor minimal to avoid import errors in demo mode.
        """
        try:
            from web3 import Web3
        except Exception as e:
            raise RuntimeError("web3.py required for RealContractService") from e
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.private_key = private_key
        # TODO: load ABI and contract instance using abi_path + contract_address

    def issue(self, holder: str, vc_type: str, cid_hash: str, expires_at: Optional[int] = None) -> Dict[str, Any]:
        raise NotImplementedError("RealContractService.issue not implemented")

    def revoke(self, vc_id: str, reason: int = 0) -> Dict[str, Any]:
        raise NotImplementedError("RealContractService.revoke not implemented")

    def status(self, vc_id: str) -> Dict[str, Any]:
        raise NotImplementedError("RealContractService.status not implemented")

def get_contract_service():
    mode = os.getenv("CHAIN_MODE", "mock").strip().lower()
    if mode == "real":
        rpc = os.getenv("BLOCKCHAIN_RPC_URL")
        pk = os.getenv("BLOCKCHAIN_PRIVATE_KEY")
        # Optionally read ABI and address envs here
        return RealContractService(rpc, pk)
    # default to mock
    return MockContractService()