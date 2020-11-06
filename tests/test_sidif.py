'''
Created on 2020-11-06

@author: wf
'''
import unittest
from sidif.sidif import SiDIFParser


class TestSiDIFParser(unittest.TestCase):
    '''
    test the parser for the Simple Data Interchange Format
    '''
    
    def setUp(self):
        self.debug = False
        self.baseUrl = "https://raw.githubusercontent.com/BITPlan/org.sidif.triplestore/master/src/test/resources/sidif"
        pass

    def tearDown(self):
        pass

    def getExampleUris(self):
        exampleUris = ["http://foo.com/blah_blah",
             "http://foo.com/blah_blah/",
             "http://foo.com/blah_blah_(wikipedia)",
             "http://foo.com/blah_blah_(wikipedia)_(again)",
             "http://www.example.com/wpstyle/?p=364",
             "http://www.schema.org/DataType",
             "https://www.example.com/foo/?bar=baz&inga=42&quux",
             "http://✪df.ws/123",
             "http://userid:password@example.com:8080",
             "http://userid:password@example.com:8080/",
             "http://userid@example.com",
             "http://userid@example.com/",
             "http://userid@example.com:8080",
             "http://userid@example.com:8080/",
             "http://userid:password@example.com",
             "http://userid:password@example.com/",
             "http://142.42.1.1/",
             "http://142.42.1.1:8080/",
             "mailto:bob@oldcorp.example.org"
            ]
        return exampleUris;
    
    def testURLRegex(self):
        '''
        test URI Regexp - see https://mathiasbynens.be/demo/url-regex
        '''
        uriRegexp = SiDIFParser.getUriRegexp()
        # self.debug=True
        for i, url in enumerate(self.getExampleUris()):
            match = uriRegexp.match(url)
            if self.debug:
                print("%d: %s->%s" % (i, url, "✅" if match else "❌"))
            self.assertTrue(match)
            
    def testGrammars(self):
        '''
        test the grammars
        '''
        sp = SiDIFParser()
        examples = [{
            "grammar": sp.getLiteral(),
            "title": "Literals",
            "sidifs": [
            "2020-12-08",
            "1970-01-01 00:00:00",
            "0xff",
            "1",
            "3.1415926",
            "6.02e23",
            "15:46",
            "http://example.org/pic.jpg",]
        },{
            "grammar": sp.getValueGrammar(),
            "title": "Value",
            "sidifs": [
                "1 is ordinal of it",
                "2020-10-15 is startDate of it",
                "http://example.org/pic.jpg is depiction of it"
            ]
        },{
            "grammar": sp.getGrammar(),
            "title": "SiDIF",
            "sidifs": [
                "SiDIF isA DataInterchangeFormat\n",
                "Paris capital France", "Paris is capital of France\n",
                "France has capital Paris\n",
             ]
            }
        ]
        #self.debug=True
        for i, example in enumerate(examples):
            grammar = example['grammar']
            title = example['title']
            for j, sidif in enumerate(example['sidifs']):
                result, error = sp.parseWithGrammar(grammar, sidif, "%s - %d/%d" % (title, i, j))
                if self.debug and result:
                    print(result.dump())
                self.assertIsNone(error)
            
    def testIsA(self):
        url = "%s/presentation.sidif" % (self.baseUrl)
        sp = SiDIFParser(debug=self.debug)
        result, error = sp.parseUrl(url, title="Presentation")
        self.assertTrue(error is None)
    
    def testExamples(self):
        '''
        test Examples from org.sidif.triplestore
        '''
        sp = SiDIFParser(debug=self.debug)
        for example in [
            "example1.sidif", "example2.sidif", "familyTree.sidif", "graph1.sidif",
            "json_ld_manu_sporny.sidif","notation3_TonyBenn.sidif",
            "presentation.sidif",
            "rdf_cd.sidif",
            "rdf_json_anna_wilder.sidif",
            "roles.sidif",
            "royal92-14.sidif",
            # "royal92.sidif"
            "trig_bob_alice.sidif",
            "triple1.sidif", "turtle_spiderman.sidif", "typetest.sidif", "utf8.sidif", "vcard.sidif"
        ]:
            url = "%s/%s" % (self.baseUrl, example)
            result, error = sp.parseUrl(url, title=example)
            self.assertTrue(error is None)
            if self.debug and result:
                print(result.dump())
                # pprint.pprint(result.asList())


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testSiDIFParser']
    unittest.main()
