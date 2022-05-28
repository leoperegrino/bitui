"""Functions for changing the state of the TUI."""
from __future__ import annotations

import curses

from typing import NamedTuple

SEP_LEN = 1


class Box(NamedTuple):
    """Container to keep track of the frame and it's content window. The box
    frame must have it's own window otherwise writing into it wil overwrite the
    border.
    """

    frame: curses._CursesWindow
    win: curses._CursesWindow

    @classmethod
    def from_args(cls, *args: int) -> Box:
        """Create a Box with frame (`win.box`) from arguments passed to
        `curses.newwin`.
        """
        frame = curses.newwin(*args)
        frame.immedok(True)
        frame.box()

        n_lines, n_cols, *_ = args
        win = frame.derwin(n_lines - 2, n_cols - 2, 1, 1)
        win.immedok(True)

        return cls(frame, win)


def vert_split(win: curses._CursesWindow, percent: float = 0.5) -> list[Box]:
    """Equally-spaced-from-borders box with a % of stdscr's height."""
    # TODO: make this function only return the arguments to be passed to a Box,
    # this way will be easier to test.
    #
    # this function makes something like this:
    # %┌ ┌─────────────┐
    #  │ │┌───────────┐│ <- stdscr
    #  │ ││           │<--- box 1
    #  └ │└───────────┘│
    #    │┌───────────┐<--- box 2
    #    │└───────────┘│
    #    └─────────────┘
    outer_y, outer_x = win.getbegyx()
    outer_h, outer_w = win.getmaxyx()
    begin_x = outer_x + SEP_LEN

    begin_y = outer_y + SEP_LEN
    width = outer_w - 2 * begin_y

    up_height = int(percent * outer_h) - 2 * SEP_LEN
    up_box = Box.from_args(up_height, width, begin_y, begin_x)

    bot_begin_y = up_height + 3 * SEP_LEN
    bot_height = int((1 - percent) * outer_h) - 2 * SEP_LEN
    bot_box = Box.from_args(bot_height, width, bot_begin_y, begin_x)

    return [up_box, bot_box]


def horiz_split(index_n: int, of_n: int, win: curses._CursesWindow) -> Box:
    """Equally-spaced-from-blocks box."""
    # TODO: make this function only return the arguments to be passed to a Box,
    # this way will be easier to test.
    #
    # this function makes something like this:
    # ┌────────┐ <- blocks box
    # │┌┐┌┐┌┐┌┐│
    # │└┘└┘└┘└┘│
    # │    ^---- 3 of 4 box
    # └────────┘
    outer_y, outer_x = win.getbegyx()
    outer_h, outer_w = win.getmaxyx()

    height = outer_h - SEP_LEN * 2
    width = (outer_w // of_n) - 2 * SEP_LEN
    begin_x = outer_x + (width + 2 * SEP_LEN) * index_n + SEP_LEN
    begin_y = outer_y + SEP_LEN

    return Box.from_args(height, width, begin_y, begin_x)
