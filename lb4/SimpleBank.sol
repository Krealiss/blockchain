// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleBank {

    address public owner;
    mapping(address => uint256) public balances;
    mapping(address => bool) public registered;
    uint256 public totalBankBalance;

    address[] private userAddresses; // 

    struct UserInfo {
        address user;
        uint256 balance;
    }

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized: Owner only");
        _;
    }

    modifier isRegistered() {
        require(registered[msg.sender], "User not registered");
        _;
    }

    function register() public {
        require(!registered[msg.sender], "User already registered");
        
        registered[msg.sender] = true;

        userAddresses.push(msg.sender); 
    }
 
    function deposit() public payable isRegistered {
        require(msg.value > 0, "Deposit amount must be greater than 0");
        
        balances[msg.sender] += msg.value;
        
        totalBankBalance += msg.value;
    }

        function getMyBalance() public view returns (uint256) {
        return balances[msg.sender];
    }

    function withdraw(uint256 _amount) public isRegistered {
        require(balances[msg.sender] >= _amount, "Insufficient funds");

        balances[msg.sender] -= _amount;
        totalBankBalance -= _amount;
 
        payable(msg.sender).transfer(_amount);
    }

    function transfer(address _to, uint256 _amount) public isRegistered {

        require(registered[_to], "Receiver is not registered");
        require(balances[msg.sender] >= _amount, "Insufficient funds");

    
        balances[msg.sender] -= _amount;
        balances[_to] += _amount;
    }

    function getTotalBalance() public view onlyOwner returns (uint256) {
        return totalBankBalance;
    }

    function getAllUsersBalance() public view returns (UserInfo[] memory) {
        UserInfo[] memory allUsers = new UserInfo[](userAddresses.length);

        for (uint i = 0; i < userAddresses.length; i++) {
            address currentUser = userAddresses[i];
            allUsers[i] = UserInfo(currentUser, balances[currentUser]);
        }

        return allUsers;
    }
}