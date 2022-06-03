from __future__ import annotations

import curses

from typing import Any
from typing import TypeAlias
from typing import NamedTuple
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    Screen: TypeAlias = curses._CursesWindow


class Dim(NamedTuple):
    """Dimensions and position relative to a screen."""
    height: int
    width: int
    y: int = 0
    x: int = 0

    @property
    def values(self) -> tuple[int, int, int, int]:
        return (
            self.height,
            self.width,
            self.y,
            self.x,
            )

    def inner(self) -> Dim:
        """Return the `Dim` of the area inside it's borders."""
        return Dim(
            self.height - 2,
            self.width - 2,
            self.y + 1,
            self.x + 1
        )


class Window:
    """Static window to be derived from another screen."""

    def __init__(self,
                 dim: Dim,
                 derived: Screen,
                 ) -> None:
        self.dim = dim
        self.derived = derived
        self.screen = derived.derwin(*dim.values)

    @classmethod
    def frame(cls, dim: Dim, derived: Screen) -> Window:
        """Create a `Window` with it's borders."""
        frame = cls(dim, derived)
        frame.screen.box()
        frame.refresh()
        return frame

    def inner(self) -> Window:
        """Return a `Window` with the inner `Dim` of the current one."""
        return Window(self.dim.inner(), self.derived)

    def refresh(self) -> None:
        # this can fail if the window was derived from a pad, since it will
        # require the `refresh` args for the pad. Just leave it to the pad to
        # refresh.
        try:
            self.screen.refresh()
        except curses.error:
            pass


class Pad:
    """Window that can extend beyond the curses screen, providing scrolling
    feature for the content inside.
    """
    # TODO: make it scroll vertically, view_start is only for width

    def __init__(self, dim: Dim, frame_dim: Dim) -> None:

        self.screen = curses.newpad(
            dim.height,
            dim.width,
        )

        self.dim = dim
        self.frame_dim = frame_dim
        # start in the middle so it's possible to
        # create next and previous blocks
        self.view_start = dim.width // 2

    @property
    def view_start(self) -> int:
        """The leftmost part of the pad visible to the screen."""
        return self._view_start

    @view_start.setter
    def view_start(self, value: int) -> None:

        floor = 0
        ceiling = self.dim.width - self.frame_dim.width
        # clip the number between floor and ceiling
        _, start, _ = sorted((floor, value, ceiling))

        self._view_start = start

    def scroll(self, width: int = 0) -> None:
        self.view_start += width

    def refresh(self) -> None:
        h, w, y, x = self.frame_dim.values
        self.screen.refresh(
            0,
            self.view_start,
            y + 1,
            x + 1,
            y + h - 2,
            x + w - 2
        )


class Block:
    """Framed window to be used as a block representation, with content
    inside.
    """

    def __init__(self, dim: Dim, pad: Screen) -> None:
        self.frame = Window.frame(dim, pad)
        self.win = Window(dim.inner(), pad)

    def write(self, content: str):
        self.win.screen.addstr(content)


class Chain:
    """Data structure to keep track of blocks creating them on the right
    place.
    """

    def __init__(self, pad: Pad) -> None:
        self.pad = pad
        self.blocks: list[Block] = []

        self.start = pad.dim.width // 2

    def __len__(self) -> int:
        return len(self.blocks)

    def new_block(self, content: str, *, prepend: bool = False) -> None:
        # TODO: make `Dim` not hardcoded here
        h, w, y = 10, 20, 1
        x = self.start + (w + 1) * len(self)
        dim = Dim(h, w, y, x)

        block = Block(dim, self.pad.screen)
        block.write(content)

        self.blocks.append(block)


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
            chain
        )

    def refresh(self) -> None:
        self.upper_pad.refresh()
        self.lower_win.refresh()
