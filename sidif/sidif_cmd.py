"""
Created on 2026-08-11

@author: wf
"""
import argparse
import sys
from pathlib import Path

from sidif.sidif import SiDIFParser
from sidif.version import Version


class SiDIFCmd:
    """
    command line for SiDIF - currently a syntax check
    """

    def __init__(self, debug: bool = False, depth: int = None):
        self.debug = debug
        self.depth = depth
        self.parser = SiDIFParser(showErrors=False, debug=debug)

    def check(self, sidif_path: str) -> int:
        """
        syntax check the given SiDIF file

        Args:
            sidif_path(str): path to the SiDIF file to check

        Returns:
            int: 0 if the file parses, 1 on syntax error or unreadable file
        """
        path = Path(sidif_path)
        try:
            sidif_text = path.read_text()
        except OSError as ose:
            print(f"{sidif_path}: {ose}", file=sys.stderr)
            return 1
        _result, error = self.parser.parseText(
            sidif_text, title=sidif_path, depth=self.depth
        )
        if error is None:
            print(f"{sidif_path}: ok")
            return 0
        err_msg = SiDIFParser.errorMessage(sidif_path, error, depth=self.depth)
        print(err_msg, file=sys.stderr)
        return 1


def get_arg_parser() -> argparse.ArgumentParser:
    """
    get the argument parser
    """
    arg_parser = argparse.ArgumentParser(
        prog=Version.name,
        description=Version.description,
    )
    arg_parser.add_argument(
        "-d", "--debug", action="store_true", help="show debug output"
    )
    arg_parser.add_argument(
        "--depth",
        type=int,
        help="explain depth for syntax error messages",
    )
    arg_parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"{Version.name} {Version.version}",
    )
    arg_parser.add_argument(
        "files",
        nargs="+",
        help="SiDIF file(s) to syntax check",
    )
    return arg_parser


def main(argv: list = None) -> int:
    """
    main call
    """
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args(argv)
    cmd = SiDIFCmd(debug=args.debug, depth=args.depth)
    exit_code = 0
    for sidif_file in args.files:
        exit_code |= cmd.check(sidif_file)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
