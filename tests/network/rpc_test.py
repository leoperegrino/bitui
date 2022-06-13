"""Basic JSON-RPC implementation."""
from __future__ import annotations

import uuid
from unittest import mock

from bitui.network.error import RPCErrorCode
from bitui.network.rpc import RPCError
from bitui.network.rpc import RPCRequest
from bitui.network.rpc import RPCResponse


def test_request_with_uuid() -> None:
    rpc_uuid = '1'
    kwargs = {
        'method': 'method',
        'params': [1, 'param'],
        'id': rpc_uuid,
        'jsonrpc': '2.0',
    }

    with mock.patch.object(uuid, 'uuid4', lambda: rpc_uuid):
        req = RPCRequest.uuid(**kwargs)
        assert req._asdict() == kwargs


def test_response_from_json() -> None:
    error = RPCError(RPCErrorCode(-1), 'message', 'data')
    none_error_input = {'result': 1, 'error': None, 'id': 1}
    with_error_input = {'result': 1, 'error': error._asdict(), 'id': 1}
    with_error_output = {'result': 1, 'error': error, 'id': 1}

    resp = RPCResponse.from_json(none_error_input)
    assert resp._asdict() == none_error_input

    resp = RPCResponse.from_json(with_error_input)
    assert resp._asdict() == with_error_output
