from __future__ import annotations

import enum

from bitui.rpc.client import RPCConfig
from bitui.rpc.client import RPCRequest
from bitui.rpc.client import RPCResponse
from bitui.rpc.client import RPCSession


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
            raise NotImplementedError(f"{call.name.lower()} not implemented")

        rpc_request = RPCRequest.uuid(call.name.lower(), args)

        return self._rpc_session.post(rpc_request)
