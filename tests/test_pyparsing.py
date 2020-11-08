'''
Created on 2020-11-08

@author: wf
'''
import unittest
from pyparsing import oneOf, ParseException, pyparsing_common,Suppress

class TestPyParsing(unittest.TestCase):
    '''
    test py parsing issue
    '''

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testBoolean(self):
        '''
        test boolean quirk
        '''
        boolValues=["true","false","invalid"]
        expected=[True,False,None]
        booleanLiteral=oneOf(
            ["true","false"]
        ).setParseAction(lambda tok:True if tok[0]=='true' else False)
        identifier=pyparsing_common.identifier
        
        boolStatement=booleanLiteral+Suppress("is")+identifier+Suppress('of')+identifier
        for i,boolValue in enumerate(boolValues):
            boolInput=("%s is value of variable") % boolValue
            print("testing %s/%s" % (boolValue,boolInput))
            try:
                result=booleanLiteral.parseString(boolValue)
                boolResult=result[0]
            except ParseException:
                boolResult=None
            try:
                result=boolStatement.parseString(boolInput)
                boolInputResult=result[0]
                #print ("%r %s %s" % (result[0],result[1],result[2]))
            except ParseException:
                boolInputResult=None
            self.assertEqual(expected[i],boolResult)
            self.assertEqual(expected[i],boolInputResult)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()