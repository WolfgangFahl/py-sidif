"""
Created on 2026-08-11

@author: wf
"""
import tempfile
from pathlib import Path

from sidif.sidif import SiDIFParser
from sidif.sidif_cmd import main
from tests.basetest import Basetest


class TestSiDIFCmd(Basetest):
    """
    test the sidif command line
    """

    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.tmpdir = tempfile.mkdtemp(prefix="sidif_cmd_")

    def write_sidif(self, name: str, sidif_text: str) -> str:
        """
        write the given sidif text to a temporary file
        """
        sidif_path = Path(self.tmpdir) / name
        sidif_path.write_text(sidif_text)
        return str(sidif_path)

    def test_check_ok(self):
        """
        test syntax check of a valid SiDIF file
        """
        sidif_path = self.write_sidif(
            "ok.sidif",
            """John isA Person
"John Doe" is name of John
""",
        )
        exit_code = main([sidif_path])
        self.assertEqual(0, exit_code)

    def test_check_syntax_error(self):
        """
        test syntax check of an invalid SiDIF file
        """
        sidif_path = self.write_sidif(
            "broken.sidif",
            """John isA
""",
        )
        exit_code = main([sidif_path])
        self.assertEqual(1, exit_code)

    def test_check_example(self):
        """
        test syntax check of a shipped sidif_examples file
        """
        example_path = Path(SiDIFParser.examples_path()) / "example1.sidif"
        exit_code = main([str(example_path)])
        self.assertEqual(0, exit_code)

    def test_check_missing_file(self):
        """
        test syntax check of a non-existing file
        """
        exit_code = main([str(Path(self.tmpdir) / "missing.sidif")])
        self.assertEqual(1, exit_code)
