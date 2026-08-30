// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract OrcaoptaLedger {
    struct Entry {
        address node;
        string message;
        uint256 timestamp;
    }

    Entry[] public entries;

    event Logged(address indexed node, string message, uint256 timestamp);

    function log(string calldata message) external {
        entries.push(Entry(msg.sender, message, block.timestamp));
        emit Logged(msg.sender, message, block.timestamp);
    }

    function getEntry(uint256 index) external view returns (address, string memory, uint256) {
        Entry memory e = entries[index];
        return (e.node, e.message, e.timestamp);
    }

    function count() external view returns (uint256) {
        return entries.length;
    }
}
