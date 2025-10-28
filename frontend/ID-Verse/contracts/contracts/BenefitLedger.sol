// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract BenefitLedger {
    event BenefitGranted(address indexed holder, uint256 schemeId, uint256 amount, string metaCID, uint64 timestamp, address grantedBy);

    function grantBenefit(address holder, uint256 schemeId, uint256 amount, string calldata metaCID) external {
        emit BenefitGranted(holder, schemeId, amount, metaCID, uint64(block.timestamp), msg.sender);
    }
}
