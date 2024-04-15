// SPDX-License-Identifier: UNLICENSED

pragma solidity >=0.7.0 <0.9.0;
pragma experimental ABIEncoderV2;

contract Message {
    struct EncMessage {
        string msgid;
        address sender;
        address receiver;
        bytes session_key;
        bytes nonce;
        bytes tag;
        bytes context;
    }

    string[] public Msgids;

    mapping(string => EncMessage) public Msgs;

    function addMessage(
        string memory _id,
        address _sender,
        address _receiver,
        bytes memory _sskey,
        bytes memory _nonce,
        bytes memory _tag
    ) public {
        EncMessage memory new_msg;
        new_msg.msgid = _id;
        new_msg.sender = _sender;
        new_msg.receiver = _receiver;
        new_msg.session_key = _sskey;
        new_msg.nonce = _nonce;
        new_msg.tag = _tag;
        new_msg.context = new bytes(0);
        Msgs[_id] = new_msg;
        Msgids.push(_id);
    }

    function getMsgids() public view returns (string memory) {
        return Msgids[Msgids.length - 1];
    }

    function addMessageCxt(string memory _id, bytes memory data) public {
        if (Msgs[_id].sender == msg.sender) {
            Msgs[_id].context = abi.encodePacked(Msgs[_id].context, data);
        }
        return;
    }

    function getMessageConf(string memory _id)
        public
        view
        returns (
            bytes memory,
            bytes memory,
            bytes memory
        )
    {
        if (
            msg.sender == Msgs[_id].sender || msg.sender == Msgs[_id].receiver
        ) {
            return (Msgs[_id].session_key, Msgs[_id].nonce, Msgs[_id].tag);
        } else {
            bytes memory tmp = new bytes(0);
            return (tmp, tmp, tmp);
        }
    }

    function getCxtLength(string memory _id) public view returns (uint256) {
        if (
            msg.sender == Msgs[_id].sender || msg.sender == Msgs[_id].receiver
        ) {
            return Msgs[_id].context.length;
        } else {
            return 0;
        }
    }

    function getMessageCxt(
        string memory _id,
        uint256 _start,
        uint256 _length
    ) public view returns (bytes memory) {
        if (
            msg.sender == Msgs[_id].sender || msg.sender == Msgs[_id].receiver
        ) {
            require(_start + _length <= Msgs[_id].context.length, "Invalid slice length");
            bytes memory slice = new bytes(_length);
            for (uint256 i = 0; i < _length; i++) {
                slice[i] = Msgs[_id].context[_start + i];
            }
            return slice;
        } else {
            return new bytes(0);
        }
    }
}