// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract IssuerRegistry {
    address public admin;
    mapping(address => bool) public isIssuer;
    event IssuerAdded(address indexed issuer);
    event IssuerRemoved(address indexed issuer);

    modifier onlyAdmin() {
        require(msg.sender == admin, "only admin");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function addIssuer(address issuer) external onlyAdmin {
        isIssuer[issuer] = true;
        emit IssuerAdded(issuer);
    }

    function removeIssuer(address issuer) external onlyAdmin {
        isIssuer[issuer] = false;
        emit IssuerRemoved(issuer);
    }

    function checkIssuer(address issuer) external view returns (bool) {
        return isIssuer[issuer];
    }
}
