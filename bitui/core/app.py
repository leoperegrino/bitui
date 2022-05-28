"""A controller for the application, managing state and applying changes.
"""
from __future__ import annotations

import enum
import time

from typing import Any

from bitui.rpc.btc import Calls
from bitui.rpc.btc import BitcoinAPI
from bitui.rpc.client import RPCConfig
from bitui.screen import state
from bitui.screen import controller
from bitui.screen.state import TUIState


class Action(enum.Enum):
    RUN = enum.auto()
    QUIT = enum.auto()


class App:

    def __init__(self,
                 stdscr: state.curses._CursesWindow,
                 rpc_config: RPCConfig
                 ) -> None:
        stdscr.refresh()
        self._state = TUIState.default(stdscr)
        self._api = BitcoinAPI(rpc_config)

    def query_chain(self) -> None:
        """Queries `blockchaininfo`."""
        info = self._api.method(Calls.GETBLOCKCHAININFO)
        self._state.chain_info.update(info.result)

    def display_summary(self) -> None:
        summary = _summary_info(self._state.chain_info)
        self._state.info_box.win.addstr(summary)

    def query_block(self, height: int) -> dict[Any, Any]:
        block_hash = self._api.method(Calls.GETBLOCKHASH, [height]).result
        block = self._api.method(Calls.GETBLOCK, [block_hash])
        return block.result

    def display_last_blocks(self, n_blocks: int) -> None:
        # TODO: refactor
        self._state.blocks.clear()
        height = self._state.chain_info["blocks"]
        start = max(0, height - n_blocks)
        block_range = range(start, height)
        win = self._state.blocks_box.win

        for idx, block_h in enumerate(block_range):
            info = self.query_block(block_h)
            block_box = controller.horiz_split(idx, n_blocks, win)
            block_box.win.addstr(_block_info(info))
            self._state.blocks.append(block_box)

    def tick(self, seconds: float = 0.05) -> None:
        """Sleeps for `seconds`. Sets framerate and slows down CPU usage."""
        time.sleep(seconds)

    def redraw(self) -> None:
        pass

    def get_input(self) -> Action:
        try:
            key = self._state.stdscr.get_wch()
        except state.curses.error:
            pass
        else:
            if key == "q":
                return Action.QUIT
            elif key == state.curses.KEY_RESIZE:
                state.curses.update_lines_cols()
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
