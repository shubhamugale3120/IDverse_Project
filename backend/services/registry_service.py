# backend/services/registry_service.py
# Blockchain registry service for Verifiable Credentials
# Supports both mock and real blockchain implementations

import os
import json
import hashlib
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from datetime import datetime

class RegistryServiceInterface(ABC):
    """Abstract interface for blockchain registry operations"""
    
    @abstractmethod
    def register_credential(self, vc_id: str, cid: str, issuer_did: str) -> str:
        """Register a credential on blockchain and return transaction hash"""
        pass
    
    @abstractmethod
    def revoke_credential(self, vc_id: str, reason: str = None) -> str:
        """Revoke a credential on blockchain and return transaction hash"""
        pass
    
    @abstractmethod
    def get_credential_status(self, vc_id: str) -> Dict[str, Any]:
        """Get credential status from blockchain"""
        pass
    
    @abstractmethod
    def is_credential_registered(self, vc_id: str) -> bool:
        """Check if credential is registered on blockchain"""
        pass


class MockRegistryService(RegistryServiceInterface):
    """
    Mock blockchain registry service for development and testing
    Simulates blockchain operations without actual network calls
    """
    
    def __init__(self):
        # Mock registry storage
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._revoked_credentials: set = set()
        self._transaction_counter = 0
    
    def register_credential(self, vc_id: str, cid: str, issuer_did: str) -> str:
        """
        Mock registration: Store credential info and return mock transaction hash
        In real implementation, this would call smart contract on blockchain
        """
        # Generate mock transaction hash
        self._transaction_counter += 1
        tx_data = f"{vc_id}_{cid}_{issuer_did}_{self._transaction_counter}_{int(datetime.utcnow().timestamp())}"
        tx_hash = f"0x{hashlib.sha256(tx_data.encode()).hexdigest()[:40]}"
        
        # Store in mock registry
        self._registry[vc_id] = {
            "vc_id": vc_id,
            "cid": cid,
            "issuer_did": issuer_did,
            "tx_hash": tx_hash,
            "registered_at": datetime.utcnow().isoformat(),
            "is_revoked": False,
            "revoked_at": None,
            "revocation_reason": None
        }
        
        return tx_hash
    
    def revoke_credential(self, vc_id: str, reason: str = None) -> str:
        """
        Mock revocation: Mark credential as revoked and return mock transaction hash
        In real implementation, this would call smart contract revocation function
        """
        if vc_id not in self._registry:
            raise ValueError(f"Credential {vc_id} not found in registry")
        
        # Generate mock revocation transaction hash
        self._transaction_counter += 1
        tx_data = f"revoke_{vc_id}_{reason}_{self._transaction_counter}_{int(datetime.utcnow().timestamp())}"
        tx_hash = f"0x{hashlib.sha256(tx_data.encode()).hexdigest()[:40]}"
        
        # Update registry entry
        self._registry[vc_id]["is_revoked"] = True
        self._registry[vc_id]["revoked_at"] = datetime.utcnow().isoformat()
        self._registry[vc_id]["revocation_reason"] = reason
        self._registry[vc_id]["revocation_tx_hash"] = tx_hash
        
        # Add to revoked set
        self._revoked_credentials.add(vc_id)
        
        return tx_hash
    
    def get_credential_status(self, vc_id: str) -> Dict[str, Any]:
        """
        Mock status check: Return credential status from mock registry
        In real implementation, this would query smart contract
        """
        if vc_id not in self._registry:
            return {
                "vc_id": vc_id,
                "is_registered": False,
                "is_revoked": False,
                "error": "Credential not found"
            }
        
        credential = self._registry[vc_id]
        return {
            "vc_id": vc_id,
            "is_registered": True,
            "is_revoked": credential["is_revoked"],
            "registered_at": credential["registered_at"],
            "revoked_at": credential["revoked_at"],
            "revocation_reason": credential["revocation_reason"],
            "tx_hash": credential["tx_hash"],
            "issuer_did": credential["issuer_did"],
            "cid": credential["cid"]
        }
    
    def is_credential_registered(self, vc_id: str) -> bool:
        """Check if credential is registered in mock registry"""
        return vc_id in self._registry and not self._registry[vc_id]["is_revoked"]


class RealRegistryService(RegistryServiceInterface):
    """
    Real blockchain registry service using Web3
    Connects to actual blockchain for credential registration and verification
    """
    
    def __init__(self, rpc_url: str = None, contract_address: str = None, private_key: str = None):
        """
        Initialize real blockchain registry service
        rpc_url: Blockchain RPC endpoint
        contract_address: Smart contract address
        private_key: Private key for signing transactions
        """
        try:
            from web3 import Web3
            self.Web3 = Web3
        except ImportError:
            raise ImportError("web3 library not installed. Run: pip install web3")
        
        # Configuration
        self.rpc_url = rpc_url or os.getenv('BLOCKCHAIN_RPC_URL', 'http://localhost:8545')
        self.contract_address = contract_address or os.getenv('REGISTRY_CONTRACT_ADDRESS')
        self.private_key = private_key or os.getenv('BLOCKCHAIN_PRIVATE_KEY')
        
        if not self.contract_address:
            raise ValueError("Contract address must be provided")
        if not self.private_key:
            raise ValueError("Private key must be provided")
        
        # Initialize Web3 connection
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Check connection
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to blockchain at {self.rpc_url}")
        
        # Load contract ABI (simplified for example)
        self.contract_abi = [
            {
                "inputs": [
                    {"name": "vcId", "type": "string"},
                    {"name": "cid", "type": "string"},
                    {"name": "issuerDid", "type": "string"}
                ],
                "name": "registerCredential",
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "vcId", "type": "string"},
                    {"name": "reason", "type": "string"}
                ],
                "name": "revokeCredential",
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "vcId", "type": "string"}],
                "name": "getCredentialStatus",
                "outputs": [
                    {"name": "isRegistered", "type": "bool"},
                    {"name": "isRevoked", "type": "bool"},
                    {"name": "registeredAt", "type": "uint256"},
                    {"name": "revokedAt", "type": "uint256"},
                    {"name": "issuerDid", "type": "string"},
                    {"name": "cid", "type": "string"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        # Initialize contract
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )
        
        # Get account from private key
        self.account = self.w3.eth.account.from_key(self.private_key)
    
    def register_credential(self, vc_id: str, cid: str, issuer_did: str) -> str:
        """
        Register credential on real blockchain
        Returns transaction hash
        """
        try:
            # Build transaction
            transaction = self.contract.functions.registerCredential(
                vc_id, cid, issuer_did
            ).build_transaction({
                'from': self.account.address,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                return receipt.transactionHash.hex()
            else:
                raise RuntimeError("Transaction failed")
                
        except Exception as e:
            raise RuntimeError(f"Failed to register credential: {e}")
    
    def revoke_credential(self, vc_id: str, reason: str = None) -> str:
        """
        Revoke credential on real blockchain
        Returns transaction hash
        """
        try:
            # Build transaction
            transaction = self.contract.functions.revokeCredential(
                vc_id, reason or ""
            ).build_transaction({
                'from': self.account.address,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                return receipt.transactionHash.hex()
            else:
                raise RuntimeError("Transaction failed")
                
        except Exception as e:
            raise RuntimeError(f"Failed to revoke credential: {e}")
    
    def get_credential_status(self, vc_id: str) -> Dict[str, Any]:
        """
        Get credential status from real blockchain
        Returns status information
        """
        try:
            # Call contract function
            result = self.contract.functions.getCredentialStatus(vc_id).call()
            
            is_registered, is_revoked, registered_at, revoked_at, issuer_did, cid = result
            
            return {
                "vc_id": vc_id,
                "is_registered": is_registered,
                "is_revoked": is_revoked,
                "registered_at": datetime.fromtimestamp(registered_at).isoformat() if registered_at > 0 else None,
                "revoked_at": datetime.fromtimestamp(revoked_at).isoformat() if revoked_at > 0 else None,
                "issuer_did": issuer_did,
                "cid": cid
            }
        except Exception as e:
            return {
                "vc_id": vc_id,
                "is_registered": False,
                "is_revoked": False,
                "error": f"Failed to get status: {e}"
            }
    
    def is_credential_registered(self, vc_id: str) -> bool:
        """Check if credential is registered on blockchain"""
        status = self.get_credential_status(vc_id)
        return status.get("is_registered", False) and not status.get("is_revoked", False)


def get_registry_service() -> RegistryServiceInterface:
    """
    Factory function to get registry service based on environment configuration
    Returns mock or real implementation based on CHAIN_MODE setting
    """
    chain_mode = os.getenv('CHAIN_MODE', 'mock').lower()
    
    if chain_mode == 'real':
        # Real blockchain configuration
        rpc_url = os.getenv('BLOCKCHAIN_RPC_URL')
        contract_address = os.getenv('REGISTRY_CONTRACT_ADDRESS')
        private_key = os.getenv('BLOCKCHAIN_PRIVATE_KEY')
        
        if not all([rpc_url, contract_address, private_key]):
            raise ValueError("Real blockchain mode requires BLOCKCHAIN_RPC_URL, REGISTRY_CONTRACT_ADDRESS, and BLOCKCHAIN_PRIVATE_KEY")
        
        return RealRegistryService(rpc_url, contract_address, private_key)
    else:
        # Default to mock for development
        return MockRegistryService()


# Example usage and testing
if __name__ == "__main__":
    # Test mock service
    print("Testing Mock Registry Service...")
    mock_service = MockRegistryService()
    
    # Register test credential
    vc_id = "vc-test-001"
    cid = "bafybeigdyrtestcid"
    issuer_did = "did:example:issuer"
    
    tx_hash = mock_service.register_credential(vc_id, cid, issuer_did)
    print(f"Registration tx hash: {tx_hash}")
    
    # Check status
    status = mock_service.get_credential_status(vc_id)
    print(f"Credential status: {status}")
    
    # Revoke credential
    revoke_tx_hash = mock_service.revoke_credential(vc_id, "Test revocation")
    print(f"Revocation tx hash: {revoke_tx_hash}")
    
    # Check status after revocation
    status_after = mock_service.get_credential_status(vc_id)
    print(f"Status after revocation: {status_after}")
    
    print("Mock registry service test completed!")
