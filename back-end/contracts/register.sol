// SPDX-License-Identifier: UNLICENSED

pragma solidity >=0.7.0 <0.9.0;
pragma experimental ABIEncoderV2;

contract Register{
    struct User{
        string name;
        address addr;
    }

    User[] public Users;

    function addUser(string memory _name, address _addr) public {
        User memory new_user;
        new_user.name = _name;
        new_user.addr = _addr;
        Users.push(new_user);
    }

    function getAllUser() public view returns (User[] memory){
        return Users;
    }
}