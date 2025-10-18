# from datetime import datetime
# from backend.extensions import db

# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(120), nullable=False)
#     email = db.Column(db.String(255), nullable=False, unique=True, index=True)
#     password_hash = db.Column(db.String(255), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
# #

# backend/model.py
# Database models for IDVerse project
from backend.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import Enum

class User(db.Model):
    """
    User model for authentication and identity management
    Stores user credentials and basic profile information
    """
    __tablename__ = "users"  # Table name in database
    
    # Primary key and basic fields
    id = db.Column(db.Integer, primary_key=True)  # Auto-incrementing primary key
    username = db.Column(db.String(150), unique=True, nullable=False)  # Unique username
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)  # Unique email with index
    password_hash = db.Column(db.String(255), nullable=False)  # Hashed password (never plain text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Account creation time
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update time
    
    # Relationships
    vc_requests = db.relationship('VCRequest', backref='requester', lazy=True)  # One-to-many: User -> VCRequests
    verifiable_credentials = db.relationship('VerifiableCredential', backref='holder', lazy=True)  # One-to-many: User -> VCs
    benefit_applications = db.relationship('BenefitApplication', backref='applicant', lazy=True)  # One-to-many: User -> Applications

    def set_password(self, password: str):
        """Hash and store password securely"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user to dictionary (exclude sensitive data)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class VCRequestStatus(Enum):
    """Enumeration for VC request statuses"""
    PENDING = "pending"      # Request submitted, awaiting processing
    APPROVED = "approved"    # Request approved, ready for issuance
    REJECTED = "rejected"    # Request rejected
    ISSUED = "issued"        # VC has been issued
    EXPIRED = "expired"      # Request expired


class VCRequest(db.Model):
    """
    Model for tracking Verifiable Credential issuance requests
    Citizens request VCs, authorities approve/reject them
    """
    __tablename__ = "vc_requests"
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Request identification
    request_id = db.Column(db.String(100), unique=True, nullable=False, index=True)  # Unique request identifier
    credential_type = db.Column(db.String(100), nullable=False)  # Type of credential (GovID, StudentCard, etc.)
    
    # Relationships
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Who requested the VC
    
    # Request data
    claims = db.Column(db.JSON, nullable=True)  # JSON field for credential claims/attributes
    subject_id = db.Column(db.String(255), nullable=True)  # Subject identifier (DID or email)
    
    # Status tracking
    status = db.Column(db.Enum(VCRequestStatus), default=VCRequestStatus.PENDING)  # Current status
    rejection_reason = db.Column(db.Text, nullable=True)  # Reason for rejection if applicable
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Request creation time
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update time
    expires_at = db.Column(db.DateTime, nullable=True)  # Request expiration time
    
    # Authority information
    approved_by = db.Column(db.String(255), nullable=True)  # Authority who approved/rejected
    approved_at = db.Column(db.DateTime, nullable=True)  # Approval/rejection time

    def to_dict(self):
        """Convert VC request to dictionary"""
        return {
            'id': self.id,
            'request_id': self.request_id,
            'credential_type': self.credential_type,
            'requester_id': self.requester_id,
            'claims': self.claims,
            'subject_id': self.subject_id,
            'status': self.status.value if self.status else None,
            'rejection_reason': self.rejection_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None
        }


class VerifiableCredential(db.Model):
    """
    Model for storing issued Verifiable Credentials
    Links to IPFS storage and blockchain registry
    """
    __tablename__ = "verifiable_credentials"
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Credential identification
    vc_id = db.Column(db.String(100), unique=True, nullable=False, index=True)  # Unique VC identifier
    credential_type = db.Column(db.String(100), nullable=False)  # Type of credential
    
    # Relationships
    holder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Who holds this VC
    request_id = db.Column(db.Integer, db.ForeignKey('vc_requests.id'), nullable=True)  # Original request
    
    # Credential data
    vc_json = db.Column(db.JSON, nullable=False)  # Full VC JSON-LD document
    claims = db.Column(db.JSON, nullable=True)  # Extracted claims for easy querying
    
    # Storage and registry
    ipfs_cid = db.Column(db.String(255), nullable=True, index=True)  # IPFS Content Identifier
    blockchain_tx_hash = db.Column(db.String(255), nullable=True, index=True)  # Blockchain transaction hash
    registry_address = db.Column(db.String(255), nullable=True)  # Smart contract address
    
    # Status and lifecycle
    is_revoked = db.Column(db.Boolean, default=False)  # Revocation status
    revoked_at = db.Column(db.DateTime, nullable=True)  # Revocation timestamp
    revoked_by = db.Column(db.String(255), nullable=True)  # Who revoked it
    revocation_reason = db.Column(db.Text, nullable=True)  # Reason for revocation
    
    # Timestamps
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)  # Issuance time
    expires_at = db.Column(db.DateTime, nullable=True)  # Expiration time
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update time

    def to_dict(self):
        """Convert VC to dictionary"""
        return {
            'id': self.id,
            'vc_id': self.vc_id,
            'credential_type': self.credential_type,
            'holder_id': self.holder_id,
            'request_id': self.request_id,
            'vc_json': self.vc_json,
            'claims': self.claims,
            'ipfs_cid': self.ipfs_cid,
            'blockchain_tx_hash': self.blockchain_tx_hash,
            'registry_address': self.registry_address,
            'is_revoked': self.is_revoked,
            'revoked_at': self.revoked_at.isoformat() if self.revoked_at else None,
            'revoked_by': self.revoked_by,
            'revocation_reason': self.revocation_reason,
            'issued_at': self.issued_at.isoformat() if self.issued_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class BenefitApplicationStatus(Enum):
    """Enumeration for benefit application statuses"""
    SUBMITTED = "submitted"    # Application submitted
    UNDER_REVIEW = "under_review"  # Being reviewed by authority
    APPROVED = "approved"      # Application approved
    REJECTED = "rejected"      # Application rejected
    DISBURSED = "disbursed"    # Benefits disbursed


class BenefitApplication(db.Model):
    """
    Model for tracking benefit/scheme applications
    Citizens apply for government benefits
    """
    __tablename__ = "benefit_applications"
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Application identification
    application_id = db.Column(db.String(100), unique=True, nullable=False, index=True)  # Unique application ID
    scheme_name = db.Column(db.String(255), nullable=False)  # Name of the benefit scheme
    
    # Relationships
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Who applied
    
    # Application data
    application_data = db.Column(db.JSON, nullable=True)  # Application form data
    supporting_documents = db.Column(db.JSON, nullable=True)  # Document references/IPFS CIDs
    
    # Status tracking
    status = db.Column(db.Enum(BenefitApplicationStatus), default=BenefitApplicationStatus.SUBMITTED)
    rejection_reason = db.Column(db.Text, nullable=True)  # Reason for rejection
    
    # Authority information
    reviewed_by = db.Column(db.String(255), nullable=True)  # Authority who reviewed
    reviewed_at = db.Column(db.DateTime, nullable=True)  # Review timestamp
    approved_at = db.Column(db.DateTime, nullable=True)  # Approval timestamp
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Application creation time
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)  # Application submission time
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update time

    def to_dict(self):
        """Convert benefit application to dictionary"""
        return {
            'id': self.id,
            'application_id': self.application_id,
            'scheme_name': self.scheme_name,
            'applicant_id': self.applicant_id,
            'application_data': self.application_data,
            'supporting_documents': self.supporting_documents,
            'status': self.status.value if self.status else None,
            'rejection_reason': self.rejection_reason,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class WalletItemStatus(Enum):
    """Enumeration for wallet item statuses"""
    ACTIVE = "active"        # Benefit is active and available
    CLAIMED = "claimed"      # Benefit has been claimed
    EXPIRED = "expired"      # Benefit has expired
    SUSPENDED = "suspended"  # Benefit is suspended


class WalletItem(db.Model):
    """
    Model for storing user's benefit entitlements in their digital wallet
    Represents approved benefits that can be claimed
    """
    __tablename__ = "wallet_items"
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Wallet item identification
    item_id = db.Column(db.String(100), unique=True, nullable=False, index=True)  # Unique wallet item ID
    
    # Relationships
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Wallet owner
    application_id = db.Column(db.Integer, db.ForeignKey('benefit_applications.id'), nullable=True)  # Related application
    
    # Benefit information
    scheme_name = db.Column(db.String(255), nullable=False)  # Name of the benefit scheme
    benefit_type = db.Column(db.String(100), nullable=False)  # Type of benefit (cash, service, etc.)
    amount = db.Column(db.Numeric(15, 2), nullable=True)  # Monetary amount if applicable
    currency = db.Column(db.String(3), default='INR')  # Currency code
    
    # Status and lifecycle
    status = db.Column(db.Enum(WalletItemStatus), default=WalletItemStatus.ACTIVE)
    
    # Blockchain and storage
    blockchain_tx_hash = db.Column(db.String(255), nullable=True, index=True)  # Approval transaction hash
    receipt_cid = db.Column(db.String(255), nullable=True)  # IPFS CID of approval receipt
    
    # Timestamps
    approved_at = db.Column(db.DateTime, default=datetime.utcnow)  # Approval time
    expires_at = db.Column(db.DateTime, nullable=True)  # Expiration time
    claimed_at = db.Column(db.DateTime, nullable=True)  # Claim time
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Creation time
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update time

    def to_dict(self):
        """Convert wallet item to dictionary"""
        return {
            'id': self.id,
            'item_id': self.item_id,
            'owner_id': self.owner_id,
            'application_id': self.application_id,
            'scheme_name': self.scheme_name,
            'benefit_type': self.benefit_type,
            'amount': float(self.amount) if self.amount else None,
            'currency': self.currency,
            'status': self.status.value if self.status else None,
            'blockchain_tx_hash': self.blockchain_tx_hash,
            'receipt_cid': self.receipt_cid,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'claimed_at': self.claimed_at.isoformat() if self.claimed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# theory==>table
# 4. backend/model.py
# Role: Defines the database models (tables).
# Models = your data schema.
# Used by auth/routes.py to save & fetch users.
# ✅ Frontend doesn’t touch this directly. But the API fields (email, password) must match frontend’s form.