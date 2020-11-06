'''
Created on 06.11.2020

@author: wf
'''
import unittest
from sidif.sidif import SiDIFParser

class TestSiDIFParser(unittest.TestCase):
    '''
    test the parser for the Simple Data Interchange Format
    '''


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testSiDIFParser(self):
        '''
        test the SiDIF parser
        '''
        sp=SiDIFParser()
        sidifs=["SiDIF isA DataInterchangeFormat","Paris is capital of France"]
        for sidif in sidifs:
            sp.parseText(sidif)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSiDIFParser']
    unittest.main()