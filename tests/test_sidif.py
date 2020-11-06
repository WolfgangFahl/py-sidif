'''
Created on 06.11.2020

@author: wf
'''
import unittest
from sidif.sidif import SiDIFParser
from pyparsing import Group,Literal,Optional,Regex,ZeroOrMore

class TestSiDIFParser(unittest.TestCase):
    '''
    test the parser for the Simple Data Interchange Format
    '''
    
    def setUp(self):
        self.debug=False
        pass

    def tearDown(self):
        pass

    def getExampleUris(self):
        exampleUris=["http://foo.com/blah_blah",
             "http://foo.com/blah_blah/",
             "http://foo.com/blah_blah_(wikipedia)",
             "http://foo.com/blah_blah_(wikipedia)_(again)",
             "http://www.example.com/wpstyle/?p=364",
             "http://www.schema.org/DataType",
            ]
        return exampleUris;
    
    def testUrlGrammar(self):
        sp=SiDIFParser()
        identifier=Regex(r"[A-Za-z_][A-Za-z_0-9]*")
        uri=Group(identifier+Literal("://")+identifier+ZeroOrMore(Regex(r"[()/.?=]")+Optional(identifier|Regex(r"[0-9]+"))))("uri")
        for i,url in enumerate(self.getExampleUris()):
            sp.parseWithGrammar(uri, url, "%d" % i)
        
    def testURLRegex(self):
        '''
        test URI Regexp - see https://mathiasbynens.be/demo/url-regex
        '''
        uriRegexp=SiDIFParser.getUriRegexp()
        for i,url in enumerate(self.getExampleUris()):
            match=uriRegexp.match(url)
            if self.debug:
                print("%d: %s->%s" % (i,url,"✅" if match else "❌"))
            self.assertTrue(match)
            
    def testSiDIFParser(self):
        '''
        test the SiDIF parser
        '''
        sp=SiDIFParser()
        sidifs=["SiDIF isA DataInterchangeFormat\n","Paris capital France","Paris is capital of France\n","France has capital Paris\n"]
        for sidif in sidifs:
            result,error=sp.parseText(sidif)
            if self.debug and result:
                print(result.dump())
            self.assertIsNone(error)
        pass
    
    def testExamples(self):
        '''
        test Examples from org.sidif.triplestore
        '''
        sp=SiDIFParser()
        baseUrl="https://raw.githubusercontent.com/BITPlan/org.sidif.triplestore/master/src/test/resources/sidif"
        for example in [
            "example1.sidif","example2.sidif","familyTree.sidif","graph1.sidif",
            "turtle_spiderman.sidif","typetest_url.sidif","utf8.sidif","vcard.sidif"
        ]:
            url="%s/%s" % (baseUrl,example)
            result,error=sp.parseUrl(url,title=example)
            #self.assertTrue(error is None)
            if self.debug and result:
                print(result.dump())
                #pprint.pprint(result.asList())

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSiDIFParser']
    unittest.main()