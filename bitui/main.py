from __future__ import annotations

import argparse
import curses

from typing import Sequence

from bitui.rpc.client import RPCConfig
from bitui.core.app import Action
from bitui.core.app import App
from bitui.utils import curses_wrapper
from bitui.utils import rpc_config_from_args


def curses_main(stdscr: curses._CursesWindow, rpc_config: RPCConfig) -> int:
    """
    High level overview of the curses application.
    To be wrapped with `curses_wrapper`, which just sets a few sane defaults.
    """
    app = App(stdscr, rpc_config)
    app.query_chain()
    app.display_summary()
    app.display_last_blocks(5)
    while True:
        app.tick()
        app.redraw()
        action = app.get_input()

        if action == Action.QUIT:
            return 0


def main(argv: Sequence[str] | None = None) -> int:
    """
    CLI entry point.
    The return value will be the program exit code.
    """
    parser = argparse.ArgumentParser(
        description="a terminal user interface for the Bitcoin blockchain",
        prog="bitui"
    )
    parser.add_argument(
        "url",
        help="RPC url",
    )
    parser.add_argument(
        "-c",
        "--chain",
        default="regtest",
        choices=["main", "test", "signet", "regtest"],
        help="Bitcoin chain to use",
    )
    parser.add_argument(
        "-u",
        "--username",
        nargs=1,
        help="username for authentication"
    )
    parser.add_argument(
        "-p",
        "--password",
        nargs=1,
        help="password for authentication"
    )
    parser.add_argument(
        "-C",
        "--cookie",
        action="store_true",
        help="use bitcoin's cookie authentication",
    )
    parser.add_argument(
        "-d",
        "--data-dir",
        default="~/.bitcoin",
        nargs="?",
        help="directory which to look for blockchain assets",
    )
    args = parser.parse_args(argv)

    rpc_config = rpc_config_from_args(args)

    exit_code = curses_wrapper(curses_main, rpc_config)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
