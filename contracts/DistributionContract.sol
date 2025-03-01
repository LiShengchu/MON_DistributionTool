// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ETHDistributor {
    address payable public owner;
    mapping(address => uint256) public deposits;

    event Deposited(address indexed depositor, uint256 amount);
    event Withdrawn(address indexed depositor, uint256 amount);
    event TransferSuccess(address indexed recipient, uint256 amount);
    event TransferFailure(address indexed recipient, uint256 amount);

    constructor() {
        owner = payable(msg.sender);
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    // 允许用户存款
    function deposit() external payable {
        deposits[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }

    // 安全提款函数
    function withdraw(uint256 amount) external {
        require(deposits[msg.sender] >= amount, "Insufficient balance");

        // 先更新状态防止重入
        deposits[msg.sender] -= amount;

        (bool success, ) = payable(msg.sender).call{value: amount}("");
        require(success, "Withdraw failed");

        emit Withdrawn(msg.sender, amount);
    }

    // 增强版分发函数（指定存款人）
    function distributeFixed(
        address depositor,
        address[] calldata recipients,
        uint256 amountPerRecipient
    ) external onlyOwner {
        uint256 requiredAmount = amountPerRecipient * recipients.length;
        require(
            deposits[depositor] >= requiredAmount,
            "Depositor balance insufficient"
        );

        uint256 successCount = 0;

        for (uint256 i = 0; i < recipients.length; i++) {
            (bool success, ) = recipients[i].call{
                value: amountPerRecipient,
                gas: 5000
            }("");

            if (success) {
                successCount++;
                emit TransferSuccess(recipients[i], amountPerRecipient);
            } else {
                emit TransferFailure(recipients[i], amountPerRecipient);
            }
        }

        // 更新存款人余额（仅扣除成功转账部分）
        uint256 totalUsed = successCount * amountPerRecipient;
        deposits[depositor] -= totalUsed;

        // 退还失败金额（自动保留在合约中）
        uint256 remaining = requiredAmount - totalUsed;
        if (remaining > 0) {
            deposits[depositor] += remaining;
        }
    }

    // 紧急停止功能
    function emergencyWithdraw(address depositor) external onlyOwner {
        uint256 amount = deposits[depositor];
        require(amount > 0, "Zero balance");

        deposits[depositor] = 0;
        (bool success, ) = depositor.call{value: amount}("");
        require(success, "Emergency withdraw failed");
    }
}