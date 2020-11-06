'''
Created on 06.11.2020

@author: wf
'''
from pyparsing import Char,CharsNotIn,Group,Keyword,LineEnd,Literal,OneOrMore,Optional
from pyparsing import ParserElement,ParseException,Regex,White,Word,ZeroOrMore
from pyparsing import alphas,alphanums,nums,printables
from keyword import iskeyword


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
        
    def getGrammar(self):
        if self.grammar is None:    
            isKeyWord=Keyword("is")
            ofKeyWord=Keyword("of")
            hasKeyWord=Keyword("has")
            identifier=Regex(r"[A-Za-z][A-Za-z_0-9]*")
            stringLiteral=Char('"')+Group(CharsNotIn('"'))('stringLiteral')+Char('"')
            literal=stringLiteral
            value=literal+isKeyWord+identifier+ofKeyWord+identifier
            idlink=identifier+identifier+identifier
            islink=identifier+isKeyWord+identifier+ofKeyWord+identifier
            haslink=identifier+hasKeyWord+identifier+identifier
            link=idlink|islink|haslink
            links=OneOrMore(link|value)
            self.grammar=links
        return self.grammar
        
    def parseText(self,sidif):
        '''
        parse the given sidif text
        
        Args:
            sidif(str): the SiDIF text to be parsed
            
        Return:
            tuple: ParseResult from pyParsing and error - one of these should be None
        '''
        result=None
        error=None
        try:
            result=self.getGrammar().parseString(sidif)
        except ParseException as pe:
            if self.debug:
                print ("error in line %d col %d: \n%s" % (pe.lineno,pe.col,pe.line))
            error=pe
        return result,error
        