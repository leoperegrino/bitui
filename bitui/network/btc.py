from __future__ import annotations

import enum

from bitui.network.rpc import RPCConfig
from bitui.network.rpc import RPCRequest
from bitui.network.rpc import RPCResponse
from bitui.network.rpc import RPCSession


class Calls(enum.Enum):
    """Implemented/supported commands"""

    GETBLOCK = enum.auto()
    GETBLOCKCHAININFO = enum.auto()
    GETBLOCKCOUNT = enum.auto()
    GETBLOCKHASH = enum.auto()


class BitcoinAPI:
    """Class for interacting specifically with the Bitcoin RPC API."""

    def __init__(self, rpc_config: RPCConfig) -> None:
        self._rpc_config = rpc_config
        self._rpc_session = RPCSession(rpc_config)

    def method(self, call: Calls, args: list[str | int] = []) -> RPCResponse:
        """Send RPC call. `cmd` must be a implemented call."""
        if not isinstance(call, Calls):
            raise NotImplementedError(f'{call} not implemented')

        rpc_request = RPCRequest.uuid(call.name.lower(), args)

        return self._rpc_session.post(rpc_request)

    # convenience methods
    def get_blockchain_info(self) -> RPCResponse.result:
        return self.method(Calls.GETBLOCKCHAININFO).result

    def get_block_hash(self, height: int) -> RPCResponse.result:
        return self.method(Calls.GETBLOCKHASH, [height]).result

    def get_block(self, block_hash: str) -> RPCResponse.result:
        return self.method(Calls.GETBLOCK, [block_hash]).result
