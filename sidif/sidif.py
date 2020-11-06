'''
Created on 06.11.2020

@author: wf
'''
from pyparsing import Char,CharsNotIn,Group,Keyword,LineEnd,OneOrMore,Optional
from pyparsing import ParserElement,ParseException,Regex,Word,ZeroOrMore,printables,pyparsing_common

from urllib.request import urlopen
import re
import sys

class SiDIFParser(object):
    '''
    Parser for SiDIF Simple Data Interchange Format 
    see http://wiki.bitplan.com/index.php/SiDIF
    '''

    def __init__(self,showErrors=True,debug=False):
        '''
        Constructor
        Args:
            showErrors(bool): True if errors should be shown/printed
            debug(bool): True if debugging should be enabled
        '''
        self.showError=showErrors
        self.debug=debug
        self.grammar=None
        ParserElement.setDefaultWhitespaceChars(" \t")
       
    @staticmethod    
    def getUriRegexp():
        '''
        get a regular expression for an URI
        '''
        # https://mathiasbynens.be/demo/url-regex
        # https://gist.github.com/dperini/729294 
        uriRegexp=(
        r"^"
        # protocol identifier
        r"(?:(?:(?:https?|ftp|file):)//|(mailto|news|nntp|telnet):)"
        # user:pass authentication
        r"(?:\S+(?::\S*)?@)?"
        r"(?:"
        # IP address exclusion
        # private & local networks
        r"(?!(?:10|127)(?:\.\d{1,3}){3})"
        r"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
        r"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
        # IP address dotted notation octets
        # excludes loopback network 0.0.0.0
        # excludes reserved space >= 224.0.0.0
        # excludes network & broadcast addresses
        # (first & last IP address of each class)
        r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
        r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
        r"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
        r"|"
        # host & domain names, may end with dot
        # can be replaced by a shortest alternative
        # r"(?![-_])(?:[-\w\u00a1-\uffff]{0,63}[^-_]\.)+"
        # r"(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)"
        # # domain name
        # r"(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*"
        r"(?:"
        r"(?:"
        r"[a-z0-9\u00a1-\uffff]"
        r"[a-z0-9\u00a1-\uffff_-]{0,62}"
        r")?"
        r"[a-z0-9\u00a1-\uffff]\."
        r")+"
        # TLD identifier name, may end with dot
        r"(?:[a-z\u00a1-\uffff]{2,}\.?)"
        r")"
        # port number (optional)
        r"(?::\d{2,5})?"
        # resource path (optional)
        r"(?:[/?#]\S*)?"
        r"$")
        compiled=re.compile(uriRegexp,re.RegexFlag.I |re.RegexFlag.UNICODE)
        return compiled
    
    def getLiteral(self):
        '''
        get the literal sub Grammar
        '''
        uri=Group(Regex(SiDIFParser.getUriRegexp()))('uri')
        integerLiteral=Group(pyparsing_common.signed_integer)('integerLiteral')
        floatingPointLiteral=Group(pyparsing_common.real)('floatingPointLiteral')
        timeLiteral=Group(Regex(r"[0-9]{2}:[0-9]{2}(:[0-9]{2})?"))('timeLiteral')
        dateLiteral=Group(Regex(r"[0-9]{4}-[0-9]{2}-[0-9]{2}"))('dateLiteral')
        dateTimeLiteral=Group(dateLiteral+Optional(timeLiteral))('dateTimeLiteral')
        stringLiteral=Group(Char('"')+Group(ZeroOrMore(CharsNotIn('"')|LineEnd()))+Char('"'))('stringLiteral')
        literal=Group(uri | stringLiteral | dateTimeLiteral | timeLiteral | floatingPointLiteral| integerLiteral )("literal")
        return literal
    
    def getValueGrammar(self):
        '''
        sub grammar for value definition
        '''
        literal=self.getLiteral()
        isKeyWord=Keyword("is")
        ofKeyWord=Keyword("of")
        identifier=Group(pyparsing_common.identifier)('identifier')   
        value=Group(literal+isKeyWord+identifier+ofKeyWord+identifier)('value')
        return value
          
    def getGrammar(self):
        if self.grammar is None:
            isKeyWord=Keyword("is")
            ofKeyWord=Keyword("of")
            hasKeyWord=Keyword("has")
            value=self.getValueGrammar()
            identifier=Group(pyparsing_common.identifier)('identifier')   
            idlink=Group(identifier+identifier+identifier)("idlink")
            islink=Group(identifier+isKeyWord+identifier+ofKeyWord+identifier)("islink")
            haslink=Group(identifier+hasKeyWord+identifier+identifier)("haslink")
            link=Group(islink|haslink|idlink)("link")
            comment=Group(Char("#")+ZeroOrMore(Word(printables))+LineEnd()|LineEnd())('comment*')
            line=Group(value|link)('line')
            links=Group(OneOrMore(line+LineEnd()|comment))('links*')
            self.grammar=links
        return self.grammar
    
    def parseUrl(self,url,title=None):
        '''
        parse the sidif text from the given url
        
        Args:
            url(str): the url to read the SiDIF text from
        '''
        sidif=urlopen(url).read().decode()
        if title is None:
            title=url
        return self.parseText(sidif,title=title)
        
    def parseWithGrammar(self,grammar,text,title=None):
        result=None
        error=None
        if title is None:
            title="?"
        try:
            result=grammar.parseString(text,parseAll=True)
        except ParseException as pe:
            if self.showError:
                print ("%s: error in line %d col %d: \n%s" % (title,pe.lineno,pe.col,pe.line),file=sys.stderr)
            #if self.debug:
                print (pe.explain(pe))
            error=pe
        return result,error
            
    def parseText(self,sidif,title=None):
        '''
        parse the given sidif text
        
        Args:
            sidif(str): the SiDIF text to be parsed
            
        Return:
            tuple: ParseResult from pyParsing and error - one of these should be None
        '''
        return self.parseWithGrammar(self.getGrammar(),sidif,title)
       
        