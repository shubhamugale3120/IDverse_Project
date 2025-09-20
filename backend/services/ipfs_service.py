# backend/services/ipfs_service.py
# ipfs == > The InterPlanetary File System (IPFS) is a protocol, hypermedia and file sharing peer-to-peer network for sharing data using a distributed hash table to store provider information.
# IPFS service for storing and retrieving Verifiable Credentials
# Supports both mock and real IPFS implementations

import os
import json
import hashlib
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class IPFSServiceInterface(ABC):
    """Abstract interface for IPFS operations"""
    
    @abstractmethod
    def upload_json(self, data: Dict[str, Any]) -> str:
        """Upload JSON data to IPFS and return CID"""
        pass
    
    @abstractmethod
    def get_json(self, cid: str) -> Optional[Dict[str, Any]]:
        """Retrieve JSON data from IPFS using CID"""
        pass
    
    @abstractmethod
    def pin_cid(self, cid: str) -> bool:
        """Pin a CID to ensure it stays available"""
        pass


class MockIPFSService(IPFSServiceInterface):
    """
    Mock IPFS service for development and testing
    Simulates IPFS operations without actual network calls
    """
    
    def __init__(self):
        # In-memory storage for mock IPFS
        self._storage: Dict[str, Dict[str, Any]] = {}
        self._pinned_cids: set = set()
    
    def upload_json(self, data: Dict[str, Any]) -> str:
        """
        Mock upload: Generate deterministic CID based on content hash
        In real implementation, this would upload to IPFS network
        """
        # Create deterministic hash from JSON content
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        content_hash = hashlib.sha256(json_str.encode('utf-8')).hexdigest()
        
        # Generate mock CID (IPFS uses base58 encoding, but we'll use hex for simplicity)
        cid = f"bafybeigdyr{content_hash[:32]}"  # Mock CID format
        
        # Store in mock storage
        self._storage[cid] = data
        
        return cid
    
    def get_json(self, cid: str) -> Optional[Dict[str, Any]]:
        """
        Mock retrieval: Get data from in-memory storage
        In real implementation, this would fetch from IPFS network
        """
        return self._storage.get(cid)
    
    def pin_cid(self, cid: str) -> bool:
        """
        Mock pinning: Mark CID as pinned
        In real implementation, this would pin to IPFS node
        """
        if cid in self._storage:
            self._pinned_cids.add(cid)
            return True
        return False


class RealIPFSService(IPFSServiceInterface):
    """
    Real IPFS service using ipfshttpclient
    Connects to actual IPFS node for storage and retrieval
    """
    
    def __init__(self, ipfs_host: str = "127.0.0.1", ipfs_port: int = 5001):
        """
        Initialize real IPFS service
        ipfs_host: IPFS node host (default: localhost)
        ipfs_port: IPFS node port (default: 5001)
        """
        try:
            import ipfshttpclient
            # Connect to IPFS node
            self.client = ipfshttpclient.connect(f"/ip4/{ipfs_host}/tcp/{ipfs_port}/http")
        except ImportError:
            raise ImportError("ipfshttpclient not installed. Run: pip install ipfshttpclient")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to IPFS node: {e}")
    
    def upload_json(self, data: Dict[str, Any]) -> str:
        """
        Upload JSON data to real IPFS network
        Returns the Content Identifier (CID)
        """
        try:
            # Convert dict to JSON string
            json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
            
            # Add to IPFS
            result = self.client.add_str(json_str)
            cid = result['Hash']
            
            return cid
        except Exception as e:
            raise RuntimeError(f"Failed to upload to IPFS: {e}")
    
    def get_json(self, cid: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve JSON data from real IPFS network
        Returns parsed JSON dict or None if not found
        """
        try:
            # Get data from IPFS
            json_str = self.client.cat(cid).decode('utf-8')
            
            # Parse JSON
            return json.loads(json_str)
        except Exception as e:
            print(f"Failed to retrieve from IPFS: {e}")
            return None
    
    def pin_cid(self, cid: str) -> bool:
        """
        Pin CID to IPFS node to ensure availability
        Returns True if successful, False otherwise
        """
        try:
            # Pin the CID
            self.client.pin.add(cid)
            return True
        except Exception as e:
            print(f"Failed to pin CID {cid}: {e}")
            return False


def get_ipfs_service() -> IPFSServiceInterface:
    """
    Factory function to get IPFS service based on environment configuration
    Returns mock or real implementation based on IPFS_MODE setting
    """
    ipfs_mode = os.getenv('IPFS_MODE', 'mock').lower()
    
    if ipfs_mode == 'real':
        # Real IPFS configuration
        ipfs_host = os.getenv('IPFS_HOST', '127.0.0.1')
        ipfs_port = int(os.getenv('IPFS_PORT', '5001'))
        return RealIPFSService(ipfs_host, ipfs_port)
    else:
        # Default to mock for development
        return MockIPFSService()


# Example usage and testing
if __name__ == "__main__":
    # Test mock service
    print("Testing Mock IPFS Service...")
    mock_service = MockIPFSService()
    
    test_data = {
        "name": "Test VC",
        "type": "VerifiableCredential",
        "issuer": "did:example:issuer"
    }
    
    # Upload test data
    cid = mock_service.upload_json(test_data)
    print(f"Uploaded CID: {cid}")
    
    # Retrieve test data
    retrieved_data = mock_service.get_json(cid)
    print(f"Retrieved data: {retrieved_data}")
    
    # Pin CID
    pinned = mock_service.pin_cid(cid)
    print(f"Pinned: {pinned}")
    
    print("Mock IPFS service test completed!")
