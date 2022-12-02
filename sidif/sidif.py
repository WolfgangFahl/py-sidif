'''
Created on 2020-11-06

@author: wf
'''
from pyparsing import CharsNotIn,Group,LineEnd,oneOf,OneOrMore,Optional
from pyparsing import ParserElement,ParseException,ParseFatalException
from pyparsing import ParseResults,Regex,Suppress,Word,ZeroOrMore
from pyparsing import hexnums,tokenMap,pyparsing_common
import pyparsing as pp

from urllib.request import urlopen
import datetime
import re
import sys

class DataInterchange():
    '''
    a data interchange
    '''
    
    def __init__(self):
        self.triples=[]
        self.comments=[]
        pass
    
    @staticmethod 
    def ofDict(pDict,context="context"):
        dif=DataInterchange()
        dif.addTriple(Triple(context,"isA","Context"))
        dif.addTriple(Triple(context,"name","it"))
        dif.addSchemaFromDict(pDict,context,context,"context")
        return dif
    
    def addLink(self,name,source,target,sourceRole,targetRole,sourceMultiple,targetMultiple):
        self.addTriple(Triple(name,"isA","TopicLink"))
        self.addTriple(Triple(name,"name","it"))
        self.addTriple(Triple(target,"target","it"))
        self.addTriple(Triple(source,"source","it"))
        self.addTriple(Triple(targetRole,"targetRole","it"))
        self.addTriple(Triple(sourceRole,"sourceRole","it"))
        self.addTriple(Triple(sourceMultiple,"sourceMultiple","it"))
        self.addTriple(Triple(targetMultiple,"targetMultiple","it"))
        
    def addTopic(self,name,context):
        topicId=self.fixId(name)
        self.addTriple(Triple(topicId,"isA","Topic"))
        self.addTriple(Triple(name,"name","it"))
        self.addTriple(Triple(context,"context","it"))
        
    def fixId(self,name):
        fixed=re.sub(r"[#@]","",name)
        return fixed
        
        
    def addSchemaFromDict(self,pDict,context,parent,parentName):    
        '''
        add schema information from the given dict
        '''
        if not isinstance(pDict,dict):
            return
        # make sure we work on properties first then other topics
        sortedKeys=sorted(pDict.keys(), key=lambda x: isinstance(pDict[x],dict))
        # loop over nodes
        for key in sortedKeys:
            value=pDict[key]
            # is the subnode a Topic or a Property?
            if isinstance(value,dict):
                # if there is an intermediate node
                # then there is a topic link
                # eg. workshop - events - event
                # https://stackoverflow.com/questions/21062781/shortest-way-to-get-first-item-of-ordereddict-in-python-3
                if len(value)==1 and isinstance(list(value.values())[0],list):
                    listNode=list(value.values())[0]
                    firstListNode=listNode[0]
                    listKey=list(value.keys())[0]
                    self.addTopic(listKey,context)
                    self.addSchemaFromDict(firstListNode,context,listKey, "Topic")
                    self.addLink(key, parent, listKey, "", key, False, len(listNode)>1)
                else:
                    # standalone topic
                    linkKey="%s%s" % (parent,key)
                    self.addTopic(key,context)
                    self.addSchemaFromDict(value,context,key,"Topic")
                    if parentName!="context":
                        self.addLink(linkKey,parent,key,"","",False,False)
            else:
                propId=self.fixId(key)
                self.addTriple(Triple(propId,"isA","Property"))
                self.addTriple(Triple(key,"name","it"))  
                valueType=type(value).__name__
                self.addTriple(Triple(valueType,"type","it"))  
                self.addTriple(Triple(parent,parentName,"it"))
    
    def addTriple(self,triple):
        '''
        add the given triple
        
        Args:
            triple(Triple): the triple to add
        '''
        self.triples.append(triple)
        
    def addComment(self,comment):
        '''
        add the given comment
        '''
        self.comments.append(comment)
        
    def asSiDIF(self):
        '''
        convert me to SiDIF notation
        '''
        sidifStr=""
        for triple in self.triples:
            sidif=triple.asSiDIF()
            sidifStr+=f"{sidif}\n"
        return sidifStr
    
    def toDictOfDicts(self):
        '''
        convert me to a dict of dicts 
        following the "it" semantics
        
        e.g.
        
        .. code-block:: python
        
               JohnDoe isA Person
               "John" is firstName of it
               "Doe"  is lastName of it
               35 is age of it
            
        will have a pseudo - triple representation of
        
        .. code-block:: python
        
            JohnDoe isA Person
            John firstName it
            Doe lastName it
            35 age it
            
        leading to a dict 
        
        .. code-block:: python
        
            {
               'JohnDoe': { 
                  'isA': Person, 
                  'firstName': John, 
                   'lastName': 'Doe'
                  'age': 35
                }
            }    
        
        Returns:
            dict: the dict of dicts representation of the triples found
        '''
        # the dict of dicts
        dod={}
        # we start with not "it" reference
        it=None
        # loop over all triples
        for triple in self.triples:
            # if this is an "it" reference 
            if triple.o=="it":
                if it is None:
                    raise Exception("Invalid it reference %s at location %d" % (triple,triple.location))
                o=triple.s
            else:
                o=triple.o
                if triple.s in dod:
                    it=dod[triple.s]
                else:
                    it={}
                    dod[triple.s]=it
            it[triple.p]=o
        return dod
        
    def __str__(self):
        text="%d triples, %d comments" % (len(self.triples),len(self.comments))
        return text

class Comment():
    '''
    a comment with it's location
    '''
    def __init__(self,comment,location):
        self.comment=comment
        self.location=location

class Triple():
    '''
    a pseudo - triple (subject,predicate,object)
    with it's location
    
    due to the "it" syntax the subject may contain the object and the real
    subject is the latest non it-reference
    '''
    
    def __init__(self,pSubject,pPredicate,pObject,location=0):
        '''
        constructor
        
        Args:
            pSubject(object): subject
            pPredicate(object): predicate
            pObject(object): object
            location(int): the location in the source text
            
        '''
        self.s=pSubject
        self.p=pPredicate
        self.o=pObject
        self.location=location
    
    def dump(self,value):    
        d="%s(%s)" % (value,type(value).__name__)
        return d
    
    def asLiteral(self,value):
        if isinstance(value,str):
            return '"%s"' % value
        elif isinstance(value,bool):
            return "true" if value else "false"
        else:
            return "%s" % value
    
    def asSiDIF(self):
        if self.o=="it":
            literal=self.asLiteral(self.s)
            line='%s is %s of it' % (literal,self.p)
        else:
            line="%s %s %s" % (self.s,self.p,self.o)
        return line
    
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
        compiled=re.compile(uriRegexp,re.IGNORECASE |re.UNICODE)
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
            raise ParseFatalException(tokenStr, location, str(ve))
        
    def convertToBoolean(self,tokenStr:str,location,token):
        '''
        convert the given token to a boolean
        '''
        try:
            tokenStr=token[0]
            if tokenStr=="true":
                return True
            elif tokenStr=="false":
                return False
        except Exception as pe:
            msg=str(pe)
        # https://stackoverflow.com/questions/13393432/raise-a-custom-exception-in-pyparsing
        raise ParseFatalException(tokenStr, location, "invalid boolean %s:%s" % (tokenStr,msg))
    
    def handleDateTimeLiteral(self,tokenStr:str,location,group):
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
            raise ParseFatalException(tokenStr, location, "invalid DateTimeLiteral %s" % tokenStr)
            
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
    
    def handleIdentifier(self,_tokenStr,_location,tokens):
        '''
        handle identifiers
        '''
        identifier=tokens['identifier'][0]
        return identifier
        
    def handleComment(self,location,tokens):
        '''
        handle the comment given comment tokens
        '''
        #tokenName=tokens.getName()
        #count=len(tokens)
        commentText=""
        for token in tokens:
            commentText+=''.join(token)
        comment=Comment(commentText,location)
        return comment
        
    def handleGroup(self,_tokenStr,_location,tokens):
        """
        handle a Group
        """
        _tokenName=tokens.getName()
        token=tokens[0]
        _innerName=token.getName()
        inner=token[0]
        return inner
    
    def addContent(self,di:DataInterchange,token,tokenName:str):
        """
        add Content to the given DataInterchange
        
        Args:
            di(DataInterchange): the datainterchange
            token: the  token to add the content for
            tokenName(str): the name of the token
        """
        if isinstance(token,ParseResults):
            if tokenName=="links" or tokenName=="comment" or tokenName=="line":
                if self.debug:
                    self.warn(f"{tokenName}: {len(token)}")
                tokenName=token.getName()
                for subtoken in token:
                    self.addContent(di,subtoken,tokenName)
            else:
                self.warn(f"parseResult {tokenName} not handled")
        elif isinstance(token,Triple):
            di.addTriple(token)
        elif isinstance(token,Comment):
            di.addComment(token)
        else:
            if self.debug:
                if not token.isspace():
                    token_type=type(token).__name__
                    self.warn(f"plain subtoken of {tokenName} type {token_type} not handled")
            pass

    def handleLines(self,_tokenStr,_location,tokens):
        '''
        handle the line derived
        '''
        di=DataInterchange()
        self.addContent(di,tokens,tokens.getName())
        return di
    
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
            #'"Paris" is capital of France'
            triple=Triple(e1,e2,e3,location)
        elif tripleKind=="idLink":
            #'Paris capital France'
            triple=Triple(e1,e2,e3,location)
        elif tripleKind=="isLink":
            #'Paris is capital of France'
            triple=Triple(e1,e2,e3,location)
        elif tripleKind=="hasLink":
            #'France has capital Paris'
            triple=Triple(e3,e2,e1,location)
        else:
            raise ParseFatalException(tokenStr, location, "invalid tripleKind %s" %tripleKind)  
        return triple
        
    
    def getLiteral(self):
        '''
        get the literal sub Grammar
        '''
        uri=Regex(SiDIFParser.getUriRegexp())('uri')
        booleanLiteral=oneOf(["true","false"]).setParseAction(self.convertToBoolean)('boolean')
        hexLiteral=(Suppress("0x")+(Word(hexnums).setParseAction(tokenMap(int, 16))))('hexLiteral')
        integerLiteral=pyparsing_common.signed_integer('integerLiteral')
        floatingPointLiteral=Group(
            pyparsing_common.sci_real|pyparsing_common.real
        ).setParseAction(self.handleGroup)('floatingPointLiteral')
        timeLiteral=Regex(r"[0-9]{2}:[0-9]{2}(:[0-9]{2})?").setParseAction(self.convertToTime)('timeLiteral')
        dateLiteral=pyparsing_common.iso8601_date.copy().setParseAction(pyparsing_common.convertToDate())('dateLiteral')
        dateTimeLiteral=Group(
            dateLiteral+Optional(timeLiteral)
        ).setParseAction(self.handleDateTimeLiteral)('dateTimeLiteral')
        stringLiteral=Group(
            Suppress('"')+ZeroOrMore(CharsNotIn('"')|LineEnd())+Suppress('"')
        ).setParseAction(self.handleStringLiteral)('stringLiteral')
        literal=Group(
            uri | stringLiteral |  booleanLiteral | hexLiteral | dateTimeLiteral | timeLiteral | floatingPointLiteral| integerLiteral 
        ).setParseAction(self.handleGroup)("literal")
        return literal
    
    def getIdentifier(self):
        """
        identifier definition
        """
        identifier=Group(
            pyparsing_common.identifier
        ).setParseAction(self.handleIdentifier)('identifier')   
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
        """
        get the grammar
        """
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
            link=Group(islink|haslink|idlink).setParseAction(self.handleGroup)("link")
            comment=Group(
                Suppress("#")+ZeroOrMore(Word(pp.pyparsing_unicode.Latin1.printables))+OneOrMore(LineEnd())|OneOrMore(LineEnd())
            ).setParseAction(self.handleComment)('comment*')
            line=Group(
                value|link
            ).setParseAction(self.handleGroup)('line')
            links=Group(
                OneOrMore(line+LineEnd()|comment)
            ).setParseAction(self.handleLines)('links*')
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
        
    def parseWithGrammar(self,grammar,text,title=None,depth:int=None):
        '''
        parse the given text with the given grammar optionally 
        labeling the parse with the given title
        
        Args:
            grammar(object): a pyparsing grammar
            text(str): the text to be parsed
            title(str): optional title
            depth(int): the explain depth to show for the errorMessage
        '''
        result=None
        error=None
        if title is None:
            title="?"
        try:
            result=grammar.parseString(text,parseAll=True)
        except ParseException as pe:
            if self.showError:
                errMsg=SiDIFParser.errorMessage(title,pe,depth=depth)
                print (errMsg,file=sys.stderr)
            error=pe
        return result,error
    
    @classmethod
    def errorMessage(cls,title:str,pe:ParseException,depth:int=None)->str:
        """
        Args:
            title(str): the title
            pe(ParseException): the exception to get the error message for
            depth(int): the explain depth to show for the errorMessage
        Returns:
            str: an error message with the explanation
        """
        msg="%s: error in line %d col %d: \n%s" % (title,pe.lineno,pe.col,pe.line)
        msg+="\n"+pe.explain(depth=depth)
        return msg
    
    def parseText(self,sidif,title=None,depth:int=None):
        '''
        parse the given sidif text
        
        Args:
            sidif(str): the SiDIF text to be parsed
            depth(int): the explain depth to show for the errorMessage
            
        Return:
            tuple: ParseResult from pyParsing and error - one of these should be None
        '''
        return self.parseWithGrammar(self.getGrammar(),sidif,title,depth=depth)
    
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