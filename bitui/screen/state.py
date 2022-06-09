from __future__ import annotations

import curses
from typing import Any
from typing import NamedTuple
from typing import TYPE_CHECKING
from typing import TypeAlias

from bitui.screen.core import Chain
from bitui.screen.core import Dim
from bitui.screen.core import Pad
from bitui.screen.core import Window


if TYPE_CHECKING:
    Screen: TypeAlias = curses._CursesWindow


class TUIState(NamedTuple):
    """Container to keep track of the state of the TUI, both
    content and blockchain info.
    """
    stdscr: Screen
    upper_pad: Pad
    upper_frame: Window
    lower_win: Window
    lower_frame: Window
    chain: Chain
    chain_info: dict[Any, Any] = {}
    selected: list[Any] = []

    @classmethod
    def init(cls, stdscr: Screen) -> TUIState:
        height = curses.LINES // 2 - 1
        width = curses.COLS - 2

        upper_dim = Dim(height, width, 1, 1)
        lower_dim = upper_dim._replace(y=height + 1)

        upper_pad = Pad(upper_dim._replace(width=width*10), upper_dim)
        lower_win = Window(lower_dim.inner(), stdscr)
        upper_frame = Window.frame(upper_dim, stdscr)
        lower_frame = Window.frame(lower_dim, stdscr)

        chain = Chain(upper_pad)

        return cls(
            stdscr,
            upper_pad,
            upper_frame,
            lower_win,
            lower_frame,
            chain,
        )

    def refresh(self) -> None:
        self.upper_pad.refresh()
        self.lower_win.refresh()
