"""
Created on 2020-11-06

@author: wf
"""

import unittest

from sidif.sidif import DataInterchange, SiDIFParser
from tests.basetest import Basetest


class TestSiDIFParser(Basetest):
    """
    test the parser for the Simple Data Interchange Format
    """

    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        # from the original java code repository
        self.baseUrl = "https://raw.githubusercontent.com/BITPlan/org.sidif.triplestore/master/src/test/resources/sidif"
        pass

    def getExampleUris(self):
        exampleUris = [
            "http://foo.com/blah_blah",
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
            "mailto:bob@oldcorp.example.org",
        ]
        return exampleUris

    def testURLRegex(self):
        """
        test URI Regexp - see https://mathiasbynens.be/demo/url-regex
        """
        uriRegexp = SiDIFParser.getUriRegexp()
        # self.debug=True
        for i, url in enumerate(self.getExampleUris()):
            match = uriRegexp.match(url)
            if self.debug:
                print("%d: %s->%s" % (i, url, "✅" if match else "❌"))
            self.assertTrue(match)

    def testGrammars(self):
        """
        test the grammars
        """
        sp = SiDIFParser()
        examples = [
            {
                "grammar": sp.getLiteral(),
                "title": "Literals",
                "sidifs": [
                    "2020-12-08",
                    "1970-01-01 18:35:23",
                    "0xff",
                    "1",
                    "true",
                    "false",
                    "3.1415926",
                    "6.02e23",
                    "15:46",
                    "http://example.org/pic.jpg",
                ],
            },
            {
                "grammar": sp.getValueGrammar(),
                "title": "Value",
                "sidifs": [
                    "1 is ordinal of it",
                    "false is started of it",
                    "2020-10-15 is startDate of it",
                    "2006-05-17 09:00:15 is timeStamp of it",
                    "0xc0 is hexValue of it",
                    "3015.76 is floatValue of it",
                    "07:59:46 is time of it",
                    "http://example.org/pic.jpg is depiction of it",
                    '"" is subtitle of it',
                ],
            },
            {
                "grammar": sp.getGrammar(),
                "title": "SiDIF",
                "sidifs": [
                    "SiDIF isA DataInterchangeFormat\n",
                    "Paris capital France",
                    "Paris is capital of France\n",
                    "France has capital Paris\n",
                    "#property Qualität",
                ],
            },
        ]
        # self.debug=True
        for i, example in enumerate(examples):
            grammar = example["grammar"]
            title = example["title"]
            for j, sidif in enumerate(example["sidifs"]):
                result, error = sp.parseWithGrammar(
                    grammar, sidif, "%s - %d/%d" % (title, i, j)
                )
                if self.debug and result:
                    print(sp.printResult(result))
                self.assertIsNone(error)

    def getPresentation(self):
        """
        get the SiDIF parse result for the presentation example
        """
        url = f"{self.baseUrl}/presentation.sidif"
        sp = SiDIFParser(debug=self.debug)
        parsed, error = sp.parseUrl(url, title="Presentation")
        self.assertTrue(error is None)
        # self.debug=True
        if self.debug:
            sp.printResult(parsed)
        dif = parsed[0]
        return dif

    def testIsA(self):
        """
        test the isA parsing
        """
        dif = self.getPresentation()
        self.assertTrue(isinstance(dif, DataInterchange))
        dod = dif.toDictOfDicts()
        if self.debug:
            print(dod)
        self.assertEqual(40, len(dod))

    def testExamples(self):
        """
        test Examples from org.sidif.triplestore
        """
        sp = SiDIFParser(debug=self.debug)
        for example, exTriples, exComments in [
            ("example1.sidif", 11, 0),
            ("example2.sidif", 15, 0),
            ("familyTree.sidif", 51, 0),
            ("graph1.sidif", 7, 1),
            ("json_ld_manu_sporny.sidif", 16, 1),
            ("notation3_TonyBenn.sidif", 4, 1),
            ("presentation.sidif", 546, 67),
            ("rdf_cd.sidif", 22, 0),
            ("rdf_json_anna_wilder.sidif", 8, 22),
            ("roles.sidif", 16, 1),
            ("royal92-14.sidif", 210, 19),
            # 62770 triples ...
            # "royal92.sidif",
            ("trig_bob_alice.sidif", 11, 24),
            ("triple1.sidif", 6, 0),
            ("turtle_spiderman.sidif", 8, 6),
            ("typetest.sidif", 62, 4),
            ("utf8.sidif", 3, 1),
            ("vcard.sidif", 31, 2),
        ]:
            url = "%s/%s" % (self.baseUrl, example)
            result, error = sp.parseUrl(url, title=example)
            self.assertTrue(error is None)
            self.assertTrue("links" in result)
            di = result["links"][0]
            foundTriples = len(di.triples)
            foundComments = len(di.comments)
            if foundTriples != exTriples or foundComments != exComments:
                sp.warn(
                    "%s: expected %d/%d triples/comments but found %d/%d"
                    % (example, exTriples, exComments, foundTriples, foundComments)
                )
                sp.printResult(result)

            self.assertEqual(exTriples, foundTriples, example)
            self.assertEqual(exComments, foundComments, example)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testSiDIFParser']
    unittest.main()
