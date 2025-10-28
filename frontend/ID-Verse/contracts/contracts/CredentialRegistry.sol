// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract CredentialRegistry {
    struct VCRef {
        address issuer;
        address holder;
        bytes32 vcType;
        bytes32 cidHash;
        uint64 issuedAt;
        uint64 expiresAt;
        bool revoked;
    }

    VCRef[] public vcs;
    mapping(address => uint256[]) public holderToVCs;
    event VCIssued(uint256 vcId, address indexed issuer, address indexed holder, bytes32 vcType, bytes32 cidHash);
    event VCRevoked(uint256 vcId, uint8 reason);

    function issue(address holder, bytes32 vcType, bytes32 cidHash, uint64 expiresAt) external returns (uint256) {
        uint64 nowTs = uint64(block.timestamp);
        VCRef memory v = VCRef(msg.sender, holder, vcType, cidHash, nowTs, expiresAt, false);
        vcs.push(v);
        uint256 id = vcs.length - 1;
        holderToVCs[holder].push(id);
        emit VCIssued(id, msg.sender, holder, vcType, cidHash);
        return id;
    }

    function revoke(uint256 vcId, uint8 reason) external {
        require(vcId < vcs.length, "invalid vc");
        VCRef storage v = vcs[vcId];
        require(msg.sender == v.issuer, "only issuer");
        v.revoked = true;
        emit VCRevoked(vcId, reason);
    }

    function getVC(uint256 vcId) external view returns (VCRef memory) {
        return vcs[vcId];
    }

    function getVCsByHolder(address holder) external view returns (uint256[] memory) {
        return holderToVCs[holder];
    }
}
