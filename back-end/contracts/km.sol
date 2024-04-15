// SPDX-License-Identifier: UNLICENSED

pragma solidity >=0.7.0 <0.9.0;
pragma experimental ABIEncoderV2;

contract KeyManagement {
    // struct defination of key
    struct PublicKey {
        bytes key;
        address[] authorization;
    }

    mapping(address => PublicKey) public Keys;

    function setAuthorization(
        address _owner,
        address _user,
        string memory _operation
    ) public {
        if (msg.sender != _owner) {
            return;
        } else {
            if (Keys[_owner].authorization.length == 0) {
                Keys[_owner].authorization.push(_user);
            } else {
                for (uint8 i = 0; i < Keys[_owner].authorization.length; i++) {
                    if (_user == Keys[_owner].authorization[i]) {
                        if (
                            keccak256(abi.encodePacked(_operation)) ==
                            keccak256(abi.encodePacked("add"))
                        ) {
                            break;
                        } else if (
                            keccak256(abi.encodePacked(_operation)) ==
                            keccak256(abi.encodePacked("del"))
                        ) {
                            Keys[_owner].authorization[i] = Keys[_owner]
                                .authorization[
                                    Keys[_owner].authorization.length - 1
                                ];
                            Keys[_owner].authorization.pop();
                            break;
                        }
                    }
                }
            }
            return;
        }
    }

    function getAuthorization(address _owner)
        public
        view
        returns (address[] memory)
    {
        address[] memory addrs;
        if (msg.sender == _owner) {
            addrs = Keys[_owner].authorization;
        }
        return addrs;
    }

    function setPubKey(address _owner, bytes memory _key) public {
        if (msg.sender != _owner) {
            return;
        } else {
            PublicKey memory new_pub_key;
            new_pub_key.key = _key;
            Keys[_owner] = new_pub_key;
        }
    }

    function checkAuthorization(address _owner) public view returns (bool) {
        if (_owner == msg.sender) {
            return true;
        } else {
            for (uint8 i = 0; i < Keys[_owner].authorization.length; i++) {
                if (msg.sender == Keys[_owner].authorization[i]) {
                    return true;
                }
            }
        }
        return false;
    }

    function getPubKey(address _owner) public view returns (bytes memory) {
        if (checkAuthorization(_owner)) {
            return Keys[_owner].key;
        }
        return new bytes(0);
    }
}