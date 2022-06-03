"""A controller for the application, managing state and applying changes.
"""
from __future__ import annotations

import curses
import enum
import time

from typing import Any
from typing import TypeAlias
from typing import TYPE_CHECKING

from bitui.rpc.btc import BitcoinAPI
from bitui.rpc.client import RPCConfig
from bitui.screen.state import TUIState

if TYPE_CHECKING:
    Screen: TypeAlias = curses._CursesWindow


class Action(enum.Enum):
    RUN = enum.auto()
    QUIT = enum.auto()


class App:

    def __init__(self,
                 stdscr: Screen,
                 rpc_config: RPCConfig
                 ) -> None:

        self._state = TUIState.init(stdscr)
        self._api = BitcoinAPI(rpc_config)

    def query_chain(self) -> None:
        """Queries `blockchaininfo`."""
        info_result = self._api.get_blockchain_info()
        self._state.chain_info.update(info_result)

    def display_summary(self) -> None:
        summary = _summary_info(self._state.chain_info)
        self._state.lower_win.screen.addstr(summary)

    def _query_block(self, height: int) -> dict[Any, Any]:
        hash_result = self._api.get_block_hash(height)
        block_result = self._api.get_block(hash_result)

        return block_result

    def display_last_blocks(self, n: int) -> None:
        height = self._state.chain_info["blocks"]

        start = max(0, height - n)

        for block_h in range(start, height):
            info = self._query_block(block_h)
            self._state.chain.new_block(_block_info(info))

    def tick(self, seconds: float = 0.01) -> None:
        """Sleeps for `seconds`. Sets framerate and slows down CPU usage."""
        time.sleep(seconds)

    def refresh(self) -> None:
        self._state.refresh()

    def get_input(self) -> Action:
        try:
            key = self._state.stdscr.get_wch()
        except curses.error:
            pass
        else:
            if key == "q":
                return Action.QUIT
            elif key == "h":
                self._state.upper_pad.scroll(-10)
            elif key == "l":
                self._state.upper_pad.scroll(10)
            elif key == curses.KEY_RESIZE:
                curses.update_lines_cols()
            elif key == -1:
                pass

        return Action.RUN


def _summary_info(info: dict[Any, Any]) -> str:
    ret = []
    for key, val in info.items():
        ret.append(f"{key} -> {val}")
    return "\n".join(ret)


def _block_info(info: dict[Any, Any]) -> str:
    ret = "\n".join(
        [
            f"height: {info['height']}",
            f"nonce: {info['nonce']}",
            f"confirmations: {info['confirmations']}",
        ]
    )

    return ret
