from __future__ import annotations

import curses

from typing import Any
from typing import NamedTuple

from bitui.screen.controller import vert_split
from bitui.screen.controller import Box


class TUIState(NamedTuple):
    """Container to keep track of the state of the TUI, both
    content and blockchain info.
    """

    stdscr: curses._CursesWindow
    info_box: Box
    blocks_box: Box
    blocks: list[Box] = []
    chain_info: dict[Any, Any] = {}
    selected: list[Any] = []

    @classmethod
    def default(cls, stdscr: curses._CursesWindow) -> TUIState:
        blocks_box, info_box = vert_split(stdscr)
        return cls(stdscr, info_box, blocks_box)
