"""
Created on 2020-11-08

@author: wf
"""

import unittest

from pyparsing import ParseException, Suppress, oneOf, pyparsing_common

from sidif.sidif import SiDIFParser


class TestPyParsing(unittest.TestCase):
    """
    test py parsing issue
    """

    def setUp(self):
        self.debug = False
        pass

    def tearDown(self):
        pass

    def testBoolean(self):
        """
        test boolean quirk
        """
        boolValues = ["true", "false", "invalid"]
        expected = [True, False, None]
        booleanLiteral = oneOf(["true", "false"]).setParseAction(
            lambda tok: True if tok[0] == "true" else False
        )
        identifier = pyparsing_common.identifier

        boolStatement = (
            booleanLiteral + Suppress("is") + identifier + Suppress("of") + identifier
        )
        sp = SiDIFParser()
        vg = sp.getValueGrammar()
        sp.showError = self.debug
        for i, boolValue in enumerate(boolValues):
            boolInput = ("%s is value of variable") % boolValue
            if self.debug:
                print("testing %s/%s" % (boolValue, boolInput))
            try:
                result = booleanLiteral.parseString(boolValue)
                boolResult = result[0]
            except ParseException:
                boolResult = None
            try:
                result = boolStatement.parseString(boolInput)
                boolInputResult = result[0]
                # print ("%r %s %s" % (result[0],result[1],result[2]))
            except ParseException:
                boolInputResult = None
            result, error = sp.parseWithGrammar(vg, boolInput, "valueGrammar")
            if error:
                vgResult = None
            else:
                if self.debug:
                    sp.printResult(result)
                vgResult = result[0].s
            self.assertEqual(expected[i], boolResult)
            self.assertEqual(expected[i], boolInputResult)
            self.assertEqual(expected[i], vgResult)
        pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
