# backend/services/signing_service.py
# Cryptographic signing service for Verifiable Credentials
# Supports multiple signing algorithms and mock implementations

import os
import json
import hashlib
from typing import Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
from datetime import datetime

class SigningServiceInterface(ABC):
    """Abstract interface for cryptographic signing operations"""
    
    @abstractmethod
    def generate_keypair(self) -> Tuple[str, str]:
        """Generate a new key pair (private_key, public_key)"""
        pass
    
    @abstractmethod
    def sign_data(self, data: Dict[str, Any], private_key: str) -> Dict[str, Any]:
        """Sign data and return signature information"""
        pass
    
    @abstractmethod
    def verify_signature(self, data: Dict[str, Any], signature: Dict[str, Any], public_key: str) -> bool:
        """Verify signature against data and public key"""
        pass
    
    @abstractmethod
    def get_issuer_did(self) -> str:
        """Get the issuer's DID (Decentralized Identifier)"""
        pass


class MockSigningService(SigningServiceInterface):
    """
    Mock signing service for development and testing
    Simulates cryptographic operations without actual cryptography
    """
    
    def __init__(self):
        # Mock issuer DID
        self.issuer_did = "did:example:issuer"
        # Mock key pair (in real implementation, these would be actual cryptographic keys)
        self.private_key = "mock_private_key_12345"
        self.public_key = "mock_public_key_67890"
    
    def generate_keypair(self) -> Tuple[str, str]:
        """
        Mock key generation: Return deterministic mock keys
        In real implementation, this would generate actual cryptographic key pairs
        """
        # Generate mock keys based on timestamp for uniqueness
        timestamp = str(int(datetime.utcnow().timestamp()))
        private_key = f"mock_private_{hashlib.sha256(timestamp.encode()).hexdigest()[:16]}"
        public_key = f"mock_public_{hashlib.sha256(timestamp.encode()).hexdigest()[:16]}"
        
        return private_key, public_key
    
    def sign_data(self, data: Dict[str, Any], private_key: str) -> Dict[str, Any]:
        """
        Mock signing: Generate deterministic signature based on data hash
        In real implementation, this would create actual cryptographic signature
        """
        # Create deterministic signature based on data content
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        content_hash = hashlib.sha256(json_str.encode('utf-8')).hexdigest()
        
        # Generate mock signature
        signature_data = f"{content_hash}_{private_key}_{int(datetime.utcnow().timestamp())}"
        mock_signature = hashlib.sha256(signature_data.encode()).hexdigest()
        
        return {
            "type": "Ed25519Signature2020",  # Mock signature type
            "created": datetime.utcnow().isoformat() + "Z",
            "verificationMethod": f"{self.issuer_did}#key-1",
            "proofPurpose": "assertionMethod",
            "jws": f"mock_jws_{mock_signature[:32]}"  # Mock JWS (JSON Web Signature)
        }
    
    def verify_signature(self, data: Dict[str, Any], signature: Dict[str, Any], public_key: str) -> bool:
        """
        Mock verification: Always return True for mock signatures
        In real implementation, this would verify actual cryptographic signature
        """
        # Mock verification - always return True
        # In real implementation, this would verify the signature against the data
        return True
    
    def get_issuer_did(self) -> str:
        """Get mock issuer DID"""
        return self.issuer_did


class Ed25519SigningService(SigningServiceInterface):
    """
    Real Ed25519 signing service using cryptography library
    Provides actual cryptographic signing for production use
    """
    
    def __init__(self, issuer_did: str = None):
        """
        Initialize Ed25519 signing service
        issuer_did: The issuer's DID (if None, will be generated)
        """
        try:
            from cryptography.hazmat.primitives.asymmetric import ed25519
            from cryptography.hazmat.primitives import serialization
            self.ed25519 = ed25519
            self.serialization = serialization
        except ImportError:
            raise ImportError("cryptography library not installed. Run: pip install cryptography")
        
        # Set issuer DID
        self.issuer_did = issuer_did or "did:example:issuer"
        
        # Load or generate key pair
        self.private_key, self.public_key = self._load_or_generate_keys()
    
    def _load_or_generate_keys(self) -> Tuple[bytes, bytes]:
        """Load existing keys or generate new ones"""
        # In production, keys should be loaded from secure storage
        # For now, we'll generate new keys each time
        private_key = self.ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        return private_key, public_key
    
    def generate_keypair(self) -> Tuple[str, str]:
        """
        Generate new Ed25519 key pair
        Returns (private_key_hex, public_key_hex)
        """
        private_key = self.ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Serialize keys to hex strings
        private_key_hex = private_key.private_bytes(
            encoding=self.serialization.Encoding.Raw,
            format=self.serialization.PrivateFormat.Raw,
            encryption_algorithm=self.serialization.NoEncryption()
        ).hex()
        
        public_key_hex = public_key.public_bytes(
            encoding=self.serialization.Encoding.Raw,
            format=self.serialization.PublicFormat.Raw
        ).hex()
        
        return private_key_hex, public_key_hex
    
    def sign_data(self, data: Dict[str, Any], private_key: str) -> Dict[str, Any]:
        """
        Sign data using Ed25519
        Returns signature information in W3C VC format
        """
        try:
            # Convert hex string back to private key object
            private_key_bytes = bytes.fromhex(private_key)
            private_key_obj = self.ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
            
            # Create data to sign (canonical JSON)
            json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
            data_bytes = json_str.encode('utf-8')
            
            # Sign the data
            signature_bytes = private_key_obj.sign(data_bytes)
            signature_hex = signature_bytes.hex()
            
            # Create signature object in W3C VC format
            return {
                "type": "Ed25519Signature2020",
                "created": datetime.utcnow().isoformat() + "Z",
                "verificationMethod": f"{self.issuer_did}#key-1",
                "proofPurpose": "assertionMethod",
                "jws": f"v={signature_hex}"  # Simplified JWS format
            }
        except Exception as e:
            raise RuntimeError(f"Failed to sign data: {e}")
    
    def verify_signature(self, data: Dict[str, Any], signature: Dict[str, Any], public_key: str) -> bool:
        """
        Verify Ed25519 signature
        Returns True if signature is valid, False otherwise
        """
        try:
            # Convert hex string back to public key object
            public_key_bytes = bytes.fromhex(public_key)
            public_key_obj = self.ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            
            # Extract signature from JWS
            jws = signature.get("jws", "")
            if not jws.startswith("v="):
                return False
            
            signature_hex = jws[2:]  # Remove "v=" prefix
            signature_bytes = bytes.fromhex(signature_hex)
            
            # Create data to verify (canonical JSON)
            json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
            data_bytes = json_str.encode('utf-8')
            
            # Verify signature
            public_key_obj.verify(signature_bytes, data_bytes)
            return True
        except Exception as e:
            print(f"Signature verification failed: {e}")
            return False
    
    def get_issuer_did(self) -> str:
        """Get issuer DID"""
        return self.issuer_did


def get_signing_service() -> SigningServiceInterface:
    """
    Factory function to get signing service based on environment configuration
    Returns mock or real implementation based on SIGN_MODE setting
    """
    sign_mode = os.getenv('SIGN_MODE', 'mock').lower()
    issuer_did = os.getenv('ISSUER_DID', 'did:example:issuer')
    
    if sign_mode == 'ed25519':
        return Ed25519SigningService(issuer_did)
    else:
        # Default to mock for development
        return MockSigningService()


# Example usage and testing
if __name__ == "__main__":
    # Test mock service
    print("Testing Mock Signing Service...")
    mock_service = MockSigningService()
    
    test_data = {
        "name": "Test VC",
        "type": "VerifiableCredential",
        "issuer": mock_service.get_issuer_did()
    }
    
    # Sign test data
    signature = mock_service.sign_data(test_data, mock_service.private_key)
    print(f"Signature: {signature}")
    
    # Verify signature
    is_valid = mock_service.verify_signature(test_data, signature, mock_service.public_key)
    print(f"Signature valid: {is_valid}")
    
    print("Mock signing service test completed!")
