'''
Created on 06.11.2020

@author: wf
'''
from pyparsing import Char,CharsNotIn,Group,LineEnd,OneOrMore,Optional
from pyparsing import ParserElement,ParseException,ParseResults,Regex,Suppress,Word,ZeroOrMore
from pyparsing import hexnums,tokenMap,printables,pyparsing_common

from urllib.request import urlopen
import datetime
import re
import sys

class Triple():
    '''
    a triple (subject,predicate,object)
    '''
    
    def __init__(self,pSubject,pPredicate,pObject):
        '''
        constructor
        
        Args:
            pSubject(object): subject
            pPredicate(object): predicate
            pObject(object): object
            
        '''
        self.s=pSubject
        self.p=pPredicate
        self.o=pObject
    
    def dump(self,value):    
        d="%s(%s)" % (value,type(value).__name__)
        return d
    
    def __str__(self):
        text="{%s,%s,%s}" % (self.dump(self.s),self.dump(self.p),self.dump(self.o))
        return text

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
        r"(?:[/?#]\S*)?")
        compiled=re.compile(uriRegexp,re.RegexFlag.I |re.RegexFlag.UNICODE)
        return compiled
    
    def convertToTime(self,tokenStr,location,token):
        '''
        convert a timeLiteral to a time
        '''
        try:
            timestr=token[0]
            fmt='%H:%M:%S' if len(timestr)==8 else '%H:%M'
            dt=datetime.datetime.strptime(timestr, fmt)
            timeResult=dt.time()
            return timeResult
        except ValueError as ve:
            raise ParseException(tokenStr, location, str(ve))
        
    def convertToBoolean(self,tokenStr,location,token):
        '''
        convert the token to a boolean
        '''
        if len(token)==1:
            if tokenStr=="true":
                return True
            elif tokenStr=="false":
                return False
        raise ParseException(tokenStr, location, "invalid boolean %s" % tokenStr)
    
    def handleDateTimeLiteral(self,tokenStr,location,group):
        '''
        handle a date time literal
        '''
        token=group[0]
        if len(token)==1:
            date=token[0]
            return date
        elif len(token)==2:
            date=token[0]
            time=token[1]
            dt=datetime.datetime(date.year,date.month,date.day,time.hour,time.minute,time.second)
            return dt
        else:
            raise ParseException(tokenStr, location, "invalid DateTimeLiteral %s" % tokenStr)
            
    def handleStringLiteral(self,_tokenStr,_location,tokens):
        '''
        handle string literals
        
        Args:
            tokens(ParseResults): the tokens for the literal
        '''
        token=tokens[0]
        if len(token)>0:
            text=token[0]
        else:
            text=''
        return text
    
    def convertToTriple(self,tokenStr,location,group):
        '''
        convert the given token to a triple
        
        Args:
            tokenStr(str): the token string
            location(object): location of the parse process
            group(ParseResults): the expected triple defining group
        ''' 
        tripleKind=group.getName()
        tokens=group[0]
        tokenCount=len(tokens)
        if tokenCount!=3:
            raise ParseException(tokenStr, location, "invalid triple %s: %d tokens found 3 expected" % (tripleKind,tokenCount))  
        e1=tokens[0]
        e2=tokens[1]
        e3=tokens[2]
        if tripleKind=="isValue":
            '"Paris" is capital of France'
            triple=Triple(e1,e2,e3)
        elif tripleKind=="idLink":
            'Paris capital France'
            triple=Triple(e1,e2,e3)
        elif tripleKind=="isLink":
            'Paris is capital of France'
            triple=Triple(e1,e2,e3)
        elif tripleKind=="hasLink":
            'France has capital Paris'
            triple=Triple(e3,e2,e1)
        else:
            raise ParseException(tokenStr, location, "invalid tripleKind %s" %tripleKind)  
        return triple
    
    def getLiteral(self):
        '''
        get the literal sub Grammar
        '''
        uri=Regex(SiDIFParser.getUriRegexp())('uri')
        booleanLiteral=Regex(r"true|false").setParseAction(self.convertToBoolean)('boolean')
        hexLiteral=Group(
            Suppress("0x")+(Word(hexnums).setParseAction(tokenMap(int, 16)))
        )('hexLiteral')
        integerLiteral=Group(
            pyparsing_common.signed_integer
        ).setParseAction(lambda tokens: tokens[0])('integerLiteral')
        floatingPointLiteral=Group(
            pyparsing_common.sci_real|pyparsing_common.real
        ).setParseAction(lambda tokens: tokens[0])('floatingPointLiteral')
        timeLiteral=Regex(r"[0-9]{2}:[0-9]{2}(:[0-9]{2})?").setParseAction(self.convertToTime)('timeLiteral')
        dateLiteral=pyparsing_common.iso8601_date.copy().setParseAction(pyparsing_common.convertToDate())('dateLiteral')
        dateTimeLiteral=Group(
            dateLiteral+Optional(timeLiteral)
        ).setParseAction(self.handleDateTimeLiteral)('dateTimeLiteral')
        stringLiteral=Group(
            Suppress('"')+ZeroOrMore(CharsNotIn('"')|LineEnd())+Suppress('"')
        ).setParseAction(self.handleStringLiteral)('stringLiteral')
        # setParseAction(lambda tokens: tokens[0] if len(tokens)>0 else '' )
        literal=Group(
            uri | stringLiteral | booleanLiteral | hexLiteral | dateTimeLiteral | timeLiteral | floatingPointLiteral| integerLiteral 
        ).setParseAction(lambda tokens: tokens[0])("literal")
        return literal
    
    def getIdentifier(self):
        identifier=Group(
            pyparsing_common.identifier
        ).setParseAction(lambda tokens: tokens[0])('identifier')   
        return identifier
    
    def getValueGrammar(self):
        '''
        sub grammar for value definition
        '''
        literal=self.getLiteral()    
        identifier=self.getIdentifier()
        value=Group(
            literal+Suppress("is")+identifier+Suppress('of')+identifier
        ).setParseAction(self.convertToTriple)('isValue')
        return value
          
    def getGrammar(self):
        if self.grammar is None:
            value=self.getValueGrammar()
            identifier=self.getIdentifier() 
            
            idlink=Group(
                identifier+identifier+identifier
            ).setParseAction(self.convertToTriple)("idLink")
            islink=Group(
                identifier+Suppress('is')+identifier+Suppress('of')+identifier
            ).setParseAction(self.convertToTriple)("isLink")
            haslink=Group(
                identifier+Suppress('has')+identifier+identifier
            ).setParseAction(self.convertToTriple)("hasLink")
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
        '''
        parse the given text with the given grammar optionally 
        labeling the parse with the given title
        
        Args:
            grammar(object): a pyparsing grammar
            text(str): the text to be parsed
            title(str): optional title
        '''
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
    
    def warn(self,msg):
        '''
        show a warning with the given message
        
        Args:
            msg(str): the warning message
        '''
        print(msg,file=sys.stderr)
        
               
    def printResult(self,pr,indent=''):
        '''
        print the given parseResult recursively
        
        Args:
            pr(object): the ParseResult to print
            indent(str): initial indentation
        '''
        if isinstance(pr,ParseResults):
            print ("%s%s:" % (indent,pr.getName()))
            for subpr in pr:
                self.printResult(subpr,indent+"  ")
        else:
            print("%s %s=%s" % (indent,type(pr).__name__,pr))