"""Basic JSON-RPC implementation."""
from __future__ import annotations

import json
import uuid
from typing import Any
from typing import NamedTuple

import requests
from requests.auth import HTTPBasicAuth

from bitui.rpc.error import RPCErrorCode

# bitcoin's rpc proTocol is primarily JSON-RPC 1.0 but
# also supports some of 2.0
# https://github.com/bitcoin/bitcoin/blob/master/src/rpc/request.cpp#L20-L27


class JSONRPCException(Exception):
    pass


class RPCConfig(NamedTuple):
    url: str
    auth: HTTPBasicAuth


class RPCRequest(NamedTuple):
    method: str
    params: list[str | int]
    rpc_id: str | None
    jsonrpc: str = '2.0'

    @classmethod
    def uuid(cls, *args: Any, **kwargs: Any) -> RPCRequest:
        """Create a new instance with a random UUID."""
        kwargs['rpc_id'] = str(uuid.uuid4())
        return cls(*args, **kwargs)


class RPCError(NamedTuple):
    code: RPCErrorCode
    message: str
    # "a Primitive or Structured value" per JSON-RPC spec
    data: Any


class RPCResponse(NamedTuple):
    result: Any
    error: RPCError | None
    rpc_id: int

    @classmethod
    def from_json(cls, json: dict[Any, Any]) -> RPCResponse:
        """Create a new instance from the `Response.json method."""
        result = json['result']
        error = json['error']
        rpc_id = json['id']

        if error:
            code = RPCErrorCode(error['code'])
            message = error['message']
            data = error.get('data')
            error = RPCError(code, message, data)

        return cls(result, error, rpc_id)


class RPCSession:
    """Class in charge of handling RPC communication."""

    def __init__(self, rpc_config: RPCConfig) -> None:

        self._session = requests.Session()
        self._session.auth = rpc_config.auth
        self._url = rpc_config.url

    def post(self, rpc_request: RPCRequest) -> RPCResponse:
        """Make a single rpc request."""

        data = json.dumps(rpc_request._asdict())

        response = self._session.post(url=self._url, data=data)

        return RPCResponse.from_json(response.json())

    def batch(self, rpc_requests: list[RPCRequest]) -> list[RPCResponse]:
        """Make a batch of requests to be sent in one HTTP POST.
        Same as `rpc_post` except it needs to increment multiples rpc id
        and match response's list order.
        """

        data = json.dumps([r._asdict() for r in rpc_requests])

        response = self._session.post(url=self._url, data=data)

        responses = [RPCResponse.from_json(r) for r in response.json()]

        # JSON-RPC spec says the batch MAY be returned in any order
        # and the client SHOULD match ids to preserve order.
        # Here we match the uuid in previous array to return it's index
        def match_idx(response: RPCResponse) -> int:
            for idx, request in enumerate(rpc_requests):
                if request.rpc_id == response.rpc_id:
                    return idx
            return 0

        responses.sort(key=match_idx)

        return responses
