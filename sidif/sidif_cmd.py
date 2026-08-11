"""
Created on 2026-08-11

@author: wf
"""
import argparse
import sys
from pathlib import Path
from urllib.request import urlopen

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
        syntax check the given SiDIF file or URL

        Args:
            sidif_path(str): path or URL of the SiDIF file to check

        Returns:
            int: 0 if the file parses, 1 on syntax error or unreadable file
        """
        try:
            # scheme://... is a URL (http, https, ftp, file - all urlopen schemes)
            # a Windows drive letter like C:\foo has no // and stays a path
            if "://" in sidif_path:
                sidif_text = urlopen(sidif_path).read().decode()
            else:
                sidif_text = Path(sidif_path).read_text()
        except OSError as ose:
            print(f"{sidif_path}: {ose}", file=sys.stderr)
            return 1
        result, error = self.parser.parseText(
            sidif_text, title=sidif_path, depth=self.depth
        )
        if error is None:
            lines = sidif_text.count("\n")
            dif = result["links"][0]
            triples = len(dif.triples)
            comments = len(dif.comments)
            print(
                f"{sidif_path}: ok - {lines} lines, {triples} triples, {comments} comments"
            )
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
