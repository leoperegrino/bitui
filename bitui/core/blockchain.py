"""Bitcoin's blockchain data structure implementation."""
from __future__ import annotations

from typing import Final
from typing import NamedTuple


MAGIC_NUMBER: Final[bytes] = b"0xD9B4BEF9"


class Header(NamedTuple):
    version: int
    prev_block_hash: str
    merkle_root_hash: str
    time: int
    bits: int
    nonce: int


class OutPoint(NamedTuple):
    hash: str
    out_index: int


class TransactionInput(NamedTuple):
    previous_output: OutPoint
    script_length: int
    signature_script: str
    sequence: int


class TransactionOutput(NamedTuple):
    value: int
    pk_script_length: int
    pk_script: str


class Components(NamedTuple):
    pass


class TransactionWitness(NamedTuple):
    witness_component_count: int
    witness_components: tuple[Components]


class BlockTransactions(NamedTuple):
    version: int
    flag: bool
    tx_in_count: int
    tx_in: tuple[TransactionInput]
    tx_out_count: int
    tx_out: tuple[TransactionOutput]
    tx_witnesses: tuple[TransactionWitness] | None
    lock_time: int


class Block(NamedTuple):
    tx_count: int
    blocksize: int
    header: Header
    transactions: BlockTransactions
    magic_number: bytes = MAGIC_NUMBER
