from __future__ import annotations

import curses
import os
import pathlib
import sys

from argparse import Namespace
from requests.auth import HTTPBasicAuth
from typing import Any
from typing import Callable

from bitui.rpc.client import RPCConfig


def _get_cookie_auth(data_dir: str, chain: str) -> HTTPBasicAuth:
    # bitcoind supports a auth cookie which is generated everytime when
    # no user/password is provided. The file contains a string in the form
    # of `user:password`, where `user` is '__cookie__' and `password` is a
    # random string.

    cookie_fp = pathlib.Path(data_dir).expanduser() / chain / ".cookie"

    with open(cookie_fp, "r", encoding="utf-8") as fp:
        username, password = fp.read().strip().split(":")

    return HTTPBasicAuth(username, password)


def rpc_config_from_args(args: Namespace) -> RPCConfig:

    if args.cookie:
        auth = _get_cookie_auth(args.data_dir, args.chain)
    else:
        auth = HTTPBasicAuth(args.username, args.password)

    return RPCConfig(args.url, auth)


def curses_wrapper(func: Callable[..., int], *args: Any, **kwds: Any) -> int:
    """Initialize all curses options in one place. Almost the same as
    `curses.wrapper`.
    """
    try:
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        stdscr.box()
        stdscr.keypad(True)
        stdscr.scrollok(True)
        stdscr.nodelay(True)

        try:
            curses.start_color()
            curses.use_default_colors()
            for i in range(1, curses.COLORS):
                curses.init_pair(i, i, -1)
        except Exception:
            pass

        if sys.version_info >= (3, 9) and hasattr(curses, "set_escdelay"):
            curses.set_escdelay(25)
        else:
            os.environ.setdefault("ESCDELAY", "25")

        return func(stdscr, *args, **kwds)
    finally:
        if "stdscr" in locals():
            stdscr.keypad(False)  # pyright: reportUnboundVariable=false
            curses.echo()
            curses.nocbreak()
            curses.endwin()
