from __future__ import annotations

import curses

from typing import Any
from typing import NamedTuple


class Widget:

    def __init__(self,
                 height: int = -1,
                 width: int = -1,
                 y: int = 1,
                 x: int = 1,
                 pad_multiplier: int = 1,
                 ) -> None:

        # default size
        if height == -1:
            height = curses.LINES // 2 - 1
        if width == -1:
            width = curses.COLS - 2

        self.frame = curses.newwin(height, width, y, x)
        self.frame.box()
        self.frame.refresh()

        # harcoded pad size for now,
        # just long enough so it can be filled with blocks
        self.pad = curses.newpad(height, width * pad_multiplier)
        # start in the middle so it's possible to
        # create next and previous blocks
        self.view_start = width * 10 // 2

    @property
    def view_start(self) -> int:
        return self._view_start

    @view_start.setter
    def view_start(self, value: int) -> None:
        _, frame_w = self.frame.getmaxyx()
        _, pad_w = self.pad.getmaxyx()

        floor = 0
        ceiling = pad_w - frame_w
        # clip the number between floor and ceiling
        _, start, _ = sorted((floor, value, ceiling))

        self._view_start = start

    def scroll(self, width: int = 0) -> None:
        self.view_start += width
        self.refresh()

    def refresh(self) -> None:
        y, x = self.frame.getbegyx()
        h, w = self.frame.getmaxyx()
        self.pad.refresh(
            0,
            self.view_start,
            y + 1,
            x + 1,
            y + h - 2,
            x + w - 2
        )


class Chain:
    def __init__(self,
                 widget: Widget,
                 blocks: list[curses._CursesWindow] = []
                 ) -> None:
        self.widget = widget
        self.blocks = blocks

    def __len__(self) -> int:
        return len(self.blocks)

    def new_block(self, content: str) -> None:
        _, pad_w = self.widget.pad.getmaxyx()
        chain_start = pad_w // 2

        h, w = (10, 20)
        y, x = (1, chain_start + (w + 1) * len(self))

        frame = self.widget.pad.derwin(h, w, y, x)
        frame.box()

        win = frame.derwin(h - 2, w - 2, 1, 1)
        win.addstr(content)

        self.blocks.append(win)


class TUIState(NamedTuple):
    """Container to keep track of the state of the TUI, both
    content and blockchain info.
    """
    stdscr: curses._CursesWindow
    upper: Widget
    lower: Widget
    chain: Chain
    chain_info: dict[Any, Any] = {}
    selected: list[Any] = []

    @classmethod
    def init(cls, stdscr: curses._CursesWindow) -> TUIState:
        upper = Widget(pad_multiplier=10)
        lower = Widget(y=curses.LINES // 2)
        blocks = Chain(upper)
        return cls(stdscr, upper, lower, blocks)

    def refresh(self) -> None:
        self.upper.refresh()
        self.lower.refresh()
