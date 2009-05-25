#!/usr/bin/python

import math
import re
import os
import sys
import socket
import base64 # for getRemoteImage
from xml.dom import minidom
from time import sleep
import stat
import datetime
import urllib2

import Image

# finished with global imports

DEBUG=False
DEBUG_CLOSE = DEBUG and True

import vision_definitions # copied from $AL_DIR/extern/python/vision_definisions.py
if DEBUG:
    import memory

from burst_util import succeed, Deferred

#########################################################################
# Constants

WEBOTS_LOCALHOST_URL = "http://localhost:9560/"

CAMERA_WHICH_PARAM = 18
CAMERA_WHICH_BOTTOM_CAMERA = 1
CAMERA_WHICH_TOP_CAMERA = 0

# ALMotion.gotoBodyAngles
INTERPOLATION_LINEAR = 0
INTERPOLATION_SMOOTH = 1

#########################################################################
# Utilities

def getip():
    return [x for x in re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', os.popen('ip addr').read()) if x[:3] != '255' and x != '127.0.0.1' and x[-3:] != '255'][0]

def compresstoprint(s, first, last):
    if len(s) < first + last + 3:
        return s
    return s[:first] + '\n...\n' + s[-last:]

def cumsum(iter):
    """ cumulative summation over an iterator """
    s = 0.0
    for t in iter:
        s += t
        yield s

def transpose(m):
    n_inner = len(m[0])
    return [[inner[i] for inner in m] for i in xrange(n_inner)]

########################################################################
# totally minimal SOAP Implementation

class XMLObject(object):

    def __init__(self, name, attrs=[], children=[]):
        self._name = name
        self._attrs = list(attrs)
        self._children = list(children)
        self._d = {}
        for c in self._children:
            if type(c) in [str, unicode]: continue
            self._d[c._name] = c

    def attributes(self, attrs):
        self._attrs = attrs
        return self
    As = attributes

    def attr(self, k, v):
        self._attrs.append((k, v))
        return self
    A = attr

    def child(self, child):
        self._children.append(child)
        if type(child) is not str:
            self._d[child._name] = child
        return self
    C = child

    def __str__(self):
        spacer = self._attrs and ' ' or ''
        return '<%s%s%s>%s</%s>' % (self._name, spacer, ' '.join('%s="%s"' % (k, v) for k, v in self._attrs), '\n'.join(str(c) for c in self._children), self._name)

    def __getitem__(self, k):
        return self._d[k]

class Requester(object):

    def __init__(self, url):
        self._url = url
        self._host, self._port, self._path = re.search('://(.*):([0-9]*)(.*)', url).groups()
        self._hostport = '%s:%s' % (self._host, self._port)
        self._port = int(self._port)

    def make(self, xmlobject):
        body = str(xmlobject)
        return """POST %(path)s HTTP/1.1
Host: %(host)s
User-Agent: mysoap/epsilon
Content-Type: text/xml; charset=utf-8
Content-Length: %(content_length)s
Connection: close
SOAPAction: ""

<?xml version="1.0" encoding="UTF-8"?>
%(body)s""" % {'path':self._path, 'host':self._hostport, 'content_length': len(body), 'body': body}

X = XMLObject

namespaces = [(lambda (a,b): (a, b[1:-1]))(n.split('=')) for n in 'xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:albroker="urn:albroker" xmlns:al="urn:aldebaran"'.split(' ')]

class SOAPObject(XMLObject):

    def __init__(self):
        super(SOAPObject, self).__init__('SOAP-ENV:Envelope',
            attrs = namespaces,
            children = [X('SOAP-ENV:Body')])

    def getbody(self):
        return self._d['SOAP-ENV:Body']
    body = property(getbody)

S = SOAPObject

#########################################################################
# Aldebaran NaoQi protocol

def getBrokerInfoObject():
    o = S()
    o.body.C(X('albroker:getBrokerInfo'))
    return o

def getInfoObject(modname):
    o = S()
    o.body.C(
        X('albroker:getInfo').C(
            X('albroker:pModuleName', [], [modname])
        )
    )
    return o

def registerBroker(name, ip, port, processId, modulePointer, isABroker=True, keepAlive=False, architecture=0):
    """
<albroker:registerBroker>
    <albroker:pBrokerToRegister>
        <name>visionmodule</name>
        <architecture>0</architecture>
        <ip>127.0.0.1</ip>
        <port>54010</port>
        <processId>1092</processId>
        <modulePointer>147822472</modulePointer>
        <isABroker>true</isABroker>
        <keepAlive>false</keepAlive>
    </albroker:pBrokerToRegister>
</albroker:registerBroker>
    """
    o = S()
    broker = X('albroker:pBrokerToRegister', [], children=[
            X(name=k, attrs=[], children=[v]) for k, v in [
                ('name', name),
                ('architecture', str(architecture)),
                ('ip', str(ip)),
                ('port', str(port)),
                ('processId', str(processId)),
                ('modulePointer', str(modulePointer)),
                ('isABroker', isABroker and 'true' or 'false'),
                ('keepAlive', keepAlive and 'true' or 'false')
            ]
        ])
    o.body.C(X('albroker:registerBroker').C(broker))
    return o

def exploreToGetModuleByNameObject(moduleName, dontLookIntoBrokerName, searchUp=True, searchDown=True):
    """
    <albroker:exploreToGetModuleByName><albroker:pModuleName>ALLogger</albroker:pModuleName><albroker:pSearchUp>true</albroker:pSearchUp><albroker:pSearchDown>true</albroker:pSearchDown><albroker:pDontLookIntoBrokerName>visionmodule</albroker:pDontLookIntoBrokerName></albroker:exploreToGetModuleByName>
    """
    o = S()
    o.body.C(X('albroker:exploreToGetModuleByName', children=[
            X('albroker:pModuleName', children=[moduleName]),
            X('albroker:pSearchUp', children=[searchUp and 'true' or 'false']),
            X('albroker:pSearchDown', children=[searchDown and 'true' or 'false']),
            X('albroker:pDontLookIntoBrokerName', children=[dontLookIntoBrokerName]),
        ]))
    return o

def serializeToSoap(x):
    """ returns an XMLObject, of name 'item' with appropriate type according to x
        array - xsi:type="Array"
        string - string
        int - int
    """
    if isinstance(x, list) or isinstance(x, tuple):
        thetype = 'Array'
        children = [serializeToSoap(c) for c in x]
    else:
        if isinstance(x, bool):
            thetype = 'xsd:boolean'
        elif isinstance(x, int):
            thetype = 'xsd:int'
        elif isinstance(x, float):
            thetype = 'xsd:float'
        else:
            thetype = 'xsd:string'
        x = str(x)
        children = [x]
    return X('item', [('xsi:type', thetype)], children)

def callNaoQiObject(mod, meth, *args):
    """ Call a method. Returns the xml
    object, you need to actually use it, with con._sendRequest, with con.call,
    or better with con.module_name.method_name()
    """
    # Example
    #"""
    #<albroker:callNaoqi>
    #<albroker:mod>NaoCam</albroker:mod>
    #<albroker:meth>register</albroker:meth>
    #<albroker:p>
    #    <item xsi:type="Array">
    #        <item xsi:type="xsd:string">testvision_GVM</item>
    #        <item xsi:type="xsd:int">2</item>
    #        <item xsi:type="xsd:int">11</item>
    #        <item xsi:type="xsd:int">15</item>
    #    </item>
    #</albroker:p></albroker:callNaoqi>
    #"""
    o = S()
    p = serializeToSoap(args) # note - this always creates an Array arround them
    o.body.C(X('albroker:callNaoqi', children=[
        X('albroker:mod', [], [mod]),
        X('albroker:meth', [], [meth]),
        X('albroker:p', [], [p])]))
    return o

def postNaoQiObject(mod, meth, *args):
    o = S()
    p = serializeToSoap(args) # note - this always creates an Array arround them
    o.body.C(X('albroker:callNaoqi2', children=[
        X('albroker:mod', [], [mod]),
        X('albroker:meth', [], [meth]),
        X('albroker:p', [], [p])]))
    return o


##################################################################
# NaoQiModule, NaoQiMethod (Top Level objects)

class NaoQiParam(object):
    
    def __init__(self, ztype, zname, zdoc):
        ztype = int(ztype)
        self.__doc__ = zdoc
        _, self._type = nao_type_dict.get(ztype, (None, ztype))
        self._name = zname

    def validate(self, v):
        # TODO
        if callable(self._type):
            try:
                self._type(v)
            except:
                return False
        return True
    
    def docstring(self):
        return '%s %s: %s' % (self._type, self._name, self.__doc__)

    def __str__(self):
        return str(self._type)

ARRAY='array'
VECTOR_STRING = 'vectorString'
nao_type_dict = {
    1: ('void', None),
    2: ('bool', lambda v: v != 'false'),
    3: ('int', int),
    4: ('float', float),
    5: ('string', str),
    6: ('ARRAY6', ARRAY),
    24: ('ARRAY24', ARRAY),
    25: ('VECTOR_STRING', VECTOR_STRING),
    }

def arrayctor(node):
    try:
        return [get_xsi_type_to_ctor(x.attributes['xsi:type'].value)(x) for x in node.firstChild.childNodes]
    except:
        import pdb; pdb.set_trace()

seen_nil_strings = set()
def return_and_print_nil(x):
    global seen_nil_strings
    # The print is for debugging purposes only, to make
    # sure the type is always matched by the same string.
    nil_str = str(x.firstChild.nodeValue)
    if nil_str not in seen_nil_strings:
        print "nil: %s" % nil_str
        seen_nil_strings.add(nil_str)
    # We return 'None' for compatibility with naoqi
    return 'None'

xsi_type_to_ctor = {
    'xsd:int': lambda x: int(x.firstChild.nodeValue),
    'xsd:float': lambda x: float(x.firstChild.nodeValue),
    'xsd:string': lambda x: str(x.firstChild.nodeValue),
    'xsd:boolean': lambda x: str(x.firstChild.nodeValue) != 'false',
    'xsd:base64Binary': lambda x: base64.decodestring(x.firstChild.nodeValue),
    'nil': return_and_print_nil,
    'Array': arrayctor
}

missing_types = set()
def get_xsi_type_to_ctor(typename):
    global missing_types
    if xsi_type_to_ctor.has_key(typename):
        return xsi_type_to_ctor[typename]
    if typename not in missing_types:
        print "missing type: %s" % typename
        missing_types.add(typename)
    return str

##################################################################

class NaoQiReturn(object):

    def __init__(self, rettype, name, doc):
        rettype = int(rettype)
        self._rettype_pprint, self._rettype = nao_type_dict.get(rettype, rettype)
        self.__doc__ = doc
        self._name = name

    def __str__(self):
        return self._rettype_pprint

    def __repr__(self):
        return '<NQRet %s>' % str(self._rettype)

    def fromNaoQiCall(self, obj):
        # TODO - check error
        ret = obj.firstChild.firstChild
        if ret.nodeName == 'faultcode':
            return ret.toprettyxml()
        if self._rettype == None:
            return None
        if self._rettype in [ARRAY, VECTOR_STRING]:
            if ret.firstChild is None:
                return []
            first_child_type = ret.firstChild.attributes['xsi:type'].value
            if first_child_type in ['xsd:float', 'xsd:int', 'xsd:string']: # some sort of exception
                return get_xsi_type_to_ctor(ret.firstChild.attributes['xsi:type'].value)(ret.firstChild)
            return [get_xsi_type_to_ctor(x.attributes['xsi:type'].value)(x) for x in ret.firstChild.childNodes]
        return self._rettype(ret.firstChild.firstChild.nodeValue)

##################################################################

class NaoQiMethod(object):

    def __init__(self, mod, name):
        self._mod = mod
        self._con = mod._con
        self._name = name
        self._has_docs = False
        self._getting_docs = False
        self.__doc__ = 'call con.%s.%s.makeHelp() to get real help.' % (self._mod._modname, self._name)

    def makeHelp(self):
        if self._has_docs:
            return succeed(None)
        d = self._getDocs()
        self._getting_docs = True
        return d

    def _getDocs(self):
        """ when first time someone accesses the doc of the method we go and get it
        also for the "hidden" parameters _params and _return """
        return self.getMethodHelp().addCallback(self._getDocs_onResponse)

    def _getDocs_onResponse(self, soapbody):
        self._has_docs = True
        doc = soapbody.firstChild.firstChild.firstChild
        if doc == None:
            self.__doc__ = 'no help supplied by module'
            self._params = []
            self._return = NaoQiReturn(rettype=1, name='', doc='') # 1 == void
            return
        # the return value is an array with:
        # index 0    - help
        # index 1   - return value
        # index 2   - params
        def nodevalues(arr):
            return [q.firstChild.nodeValue for q in arr.childNodes]
        self._params = [NaoQiParam(*nodevalues(t)) for t in doc.childNodes[2].childNodes]
        self._return = NaoQiReturn(*nodevalues(doc.childNodes[1]))
        name, docstring, module = [c.firstChild.nodeValue for c in doc.firstChild.childNodes]
        self.__doc__ = '%s %s(%s) - %s (%s)\nParameters:\n%s' % (self._return, name, ','.join(map(str, self._params)), docstring, module, ''.join(' %s\n' % p.docstring() for p in self._params))

    def getMethodHelp(self):
        return self._con._sendRequest(callNaoQiObject(self._mod._modname, 'getMethodHelp', self._name))

    def _realcall(self, args, callCreator, callback, d):
        """ handles normal and post calls. They all go through validation
        (TODO - make it optional), then it is passed through the callCreator,
        and on return through the callback and finally to the deferred d.
        """
        if len(args) != len(self._params):
            raise Exception("Wrong number of parameters: expected %s, got %s" % (len(self._params), len(args)))
        for i, (p, a) in enumerate(zip(self._params, args)):
            if not p.validate(a):
                raise Exception("Argument %s for %s is bad: type is %s, given value is %s" % (i, self._name, p, a))
        self._con._sendRequest(callCreator(self._mod._modname,
            self._name, *args)).addCallback(callback
            ).addCallback(d.callback)

    def __call__(self, *args):
        ret = Deferred()
        
        if not self._has_docs:
            self.makeHelp().addCallback(lambda _, self=self, args=args:
                self._realcall(args=args, callCreator=callNaoQiObject,
                    callback=self._call_onResponse, d=ret))
        else:
            self._realcall(args=args, callCreator=callNaoQiObject,
                callback=self._call_onResponse, d=ret)

        return ret

    def _call_onResponse(self, soapbody):
        return self._return.fromNaoQiCall(soapbody)

    def _post_onResponse(self, soapbody):
        # returns postid from a <albroker:callNaoqi2Response> wrapping an <array>
        # with fields "postid" (int), "methname" , "module name", a boolean
        # and an int (no idea the meaning of the later two)
        return int(soapbody.firstChild.firstChild.firstChild.firstChild.firstChild.data)

    def post(self, *args):
        ret = Deferred()

        if not self._has_docs:
            self.makeHelp().addCallback(lambda _, self=self, args=args:
                self._realcall(args=args, callCreator=postNaoQiObject,
                    callback=self._post_onResponse, d=ret))
        else:
            self._realcall(args=args, callCreator=postNaoQiObject,
                callback=self._post_onResponse, d=ret)

        return ret

##################################################################

class ModulesHolder(object):
    pass

class MethodHolder(object):
    pass

##################################################################

class ModulePosts(object):
    pass

class NaoQiModule(object):

    VERBOSE = True # mainly here so I can shut it down when using twisted

    def __init__(self, con, modname):
        self._con = con
        self._modname = modname
        # async? nah, don't bother right now. (everything here
        # should be twisted.. ok, it can be asynced some other way)
        self.initDeferred = Deferred() # hook for inheriting classes, will be called when init is done
        self.post = ModulePosts()
        self.methods = MethodHolder()
        self.getMethods().addCallback(self.onMethodsAvailable)

    def onMethodsAvailable(self, methods):
        self.method_names = methods
        for meth in self.method_names:
            methobj = NaoQiMethod(self, meth)
            setattr(self, meth, methobj)
            setattr(self.methods, meth, methobj)
            setattr(self.post, meth, methobj.post)
        # this actually uses one of the methods above!
        self._has_docs = False
        self.__doc__ = """ Call con.%s.makeHelp() to generate help for this module and it's methods """ % self._modname
        self.initDeferred.callback(None)

    def makeHelp(self):
        if self.VERBOSE:
            print "going to get help..",
        self._getDoc()
        for meth in self.methods.__dict__.values():
            if hasattr(meth, 'makeHelp'):
                meth.makeHelp()
        if self.VERBOSE:
            print "done"
        self._has_docs = True

    def _getDoc(self):
        """ self annihilating method """
        self.moduleHelp().addCallback(self._onGetDocReturn)

    def _onGetDocReturn(self, result):
        self.__doc__ = result[0]

    def getName(self):
        return self._modname

    def getMethods(self):
        """ returns the method names in unicode for the given module
        """
        return self._con._sendRequest(callNaoQiObject(self._modname,
                'getMethodList')).addCallback(self._getMethods_onResponse)

    def _getMethods_onResponse(self, soapbody):
        return [e.firstChild.wholeText for e in soapbody.firstChild.firstChild.firstChild.childNodes]

    def justModuleHelp(self):
        return self._con._sendRequest(callNaoQiObject(self._mod._modname, 'moduleHelp'))

DEG_TO_RAD = math.pi/180.0

class ALMotionExtended(NaoQiModule):

    def __init__(self, con):
        NaoQiModule.__init__(self, con, 'ALMotion')
        self.initDeferred.addCallback(self.onModuleInited)

    def onModuleInited(self, result):
        self.getBodyJointNames().addCallback(self.onBodyJointNames)

    def onBodyJointNames(self, joint_names):
        self._joint_names = joint_names

    def executeMove(self, moves, interp_type = INTERPOLATION_SMOOTH):
        """ Work like northern bites code using ALMotion.doMove
        """
        # minimal check just for allowed moves, not checking it is a list non zero length etc.
        if len(moves[0]) == 5 and len(moves[0][0]) == 4:
            self.executeMove20(moves, interp_type)
        elif len(moves[0]) == 2 and len(moves[0][0]) == 2:
            self.executeMoveHead(moves, interp_type)
        else:
            print "ERROR: ALMotionExtend.executeMove: unrecognized move"

    def executeMove20(self, moves, interp_type):
        """ for 20 joint moves (4 + 6 + 6 + 4)
        """
        joints = self._joint_names[2:]
        n_joints = len(joints)
        angles_matrix = transpose([[x*DEG_TO_RAD for x in list(larm)
                    + [0.0, 0.0] + list(lleg) + list(rleg) + list(rarm)
                    + [0.0, 0.0]] for larm, lleg, rleg, rarm, interp_time in moves])
        durations_matrix = [list(cumsum(interp_time for larm, lleg, rleg, rarm, interp_time in moves))] * n_joints
        duration = max(col[-1] for col in durations_matrix)
        #print repr((joints, angles_matrix, durations_matrix))
        self.doMove(joints, angles_matrix, durations_matrix, interp_type)

    def executeMoveHead(self, moves, interp_type):
        joints = self._joint_names[:2]
        n_joints = len(joints)
        angles_matrix = transpose([[x*DEG_TO_RAD for x in head] for head, interp_time in moves])
        durations_matrix = [list(cumsum(interp_time for head, interp_time in moves))] * n_joints
        self.doMove(joints, angles_matrix, durations_matrix, interp_type)

    def executeMoveByGoto(self, moves, interp_type = INTERPOLATION_SMOOTH):
        for move in moves:
            larm, lleg, rleg, rarm, interp_time = move
            curangles = self.getBodyAngles()
            joints = curangles[:2] + [x*DEG_TO_RAD for x in list(larm)
                + [0.0, 0.0] + list(lleg) + list(rleg) + list(rarm)
                + [0.0, 0.0]]
            self.gotoBodyAngles(joints, interp_time, interp_type)
  
##################################################################
# Connection (Top Level object)

def getpairs(elem):
    """ helper method for parsing DOM Elements's """
    return [(x.nodeName, x.firstChild.nodeValue) for x in elem.childNodes]

class BaseNaoQiConnection(object):

    def __init__(self, url="http://localhost:9560/", verbose = True, options=None):
        self.verbose = verbose
        self.options = options # the parsed command line options, convenient place to store them
        self._url = url
        self._req = Requester(url)
        self._is_webots = self._req._port == 9560
        self.s = None # socket to connect to broker. reusing - will it work?
        self._myip = getip()
        self._myport = 12345 # bogus - we are acting as a broker - this needs to be a seperate class
        self._error_accessing_host = False

        self.modulesDeferred = Deferred()
        self._modules_to_wait_for_init_of = None
       
        if self.options.twisted:
            # if we have twisted, use that implementation
            try:
                import twisted.internet.reactor
            except:
                pass
            else:
                print "twisted found, using self._twistedSendRequest"
                self._sendRequest = self._twistedSendRequest
                from .pynaoqi_twisted import SoapRequestFactory
                self.SoapRequestFactory = SoapRequestFactory
                NaoQiModule.VERBOSE = False

        self._initModules()
    
    def getHost(self):
        return self._req._host
    host = property(getHost)

    def _initModules(self):
        """ internal method. Initializes the list of modules and their list of methods """
        self._modules = []
        modules = []
        try:
            modules = self.getModules()
        except urllib2.URLError:
            if not self._error_accessing_host:
                print "!!! connection refused, will retry 1 second after reactor.start"
                self._error_accessing_host = True
            import twisted.internet.reactor as reactor
            reactor.callLater(1.0, self._initModules)
        for i, modname in enumerate(modules):
            if self.verbose:
                print "(%s) %s.." % (i + 1, modname),
                sys.stdout.flush()
            mod = self.getModule(modname)
            self._modules.append(mod)
        if len(modules) > 0 and self.verbose:
            print
        self.modules = ModulesHolder()
        for m in self._modules:
            self.__dict__[m.getName()] = m
            self.modules.__dict__[m.getName()] = m
        if len(self._modules) > 0:
            # assume this is the fixed number of modules.
            # this doesn't hold if we start in the middle of
            # a loading naoqi - live with it.
            self._modules_to_wait_for_init_of = len(self._modules)
            for m in self._modules:
                m.initDeferred.addCallback(self._moduleInitDone)

    def _moduleInitDone(self, _):
        self._modules_to_wait_for_init_of -= 1
        if self._modules_to_wait_for_init_of <= 0:
            self.modulesDeferred.callback(None)

    def contentLengthFromHeaders(self, headers):
        return int(re.search('Content-Length: ([0-9]+)', headers).groups()[0])

    def closeSocketFromHeaders(self, headers):
        return  re.search('Connection: (.*)', headers).groups()[0].strip() == 'close'

    def _sendRequest(self, o):
        """ sends a request, returns a Deferred, which you can do addCallback on.
        If this is in fact synchronous, your callback will be called immediately,
        otherwise it will be called upon availability of data from socket.
        """
        if self.s is None:
            self.s = socket.socket()
            self.s.connect((self._req._host, self._req._port))
        s = self.s
        tosend = self._req.make(o)
        if DEBUG:
            print "***     Sending:     ***\n%s" % tosend
        s.send(tosend)
        # get headers, read size, read the rest
        h = []
        c = None
        if DEBUG:
            print "receiving:"
        while c != '<':
            c = s.recv(1)
            if DEBUG:
                sys.stdout.write(c)
                sys.stdout.flush()
            h.append(c)
        if DEBUG:
            print
        headers = ''.join(h[:-1])
        content_length = self.contentLengthFromHeaders(headers)
        # Connection: close
        close_socket = self.closeSocketFromHeaders(headers)
        if close_socket and DEBUG_CLOSE:
            print "Will close socket"
        if DEBUG:
            print "expecting %s" % content_length
        # this loop is required for getting large stuff, like getRemoteImage (1200000~ bytes for 640x480 RGB)
        rest = []
        left = content_length - 1
        while left > 0:
            rest.append(s.recv(content_length-1))
            left -= len(rest[-1])
        if DEBUG:
            print "memory = %s" % memory.memory()
        body = h[-1] + ''.join(rest)
        if DEBUG:
            print "***     Got:          ***\n%s" % compresstoprint(headers + body, 1000, 1000)
            print "*************************"
        if close_socket:
            self.s.close()
            self.s = None
        xml = minidom.parseString(body)
        soapbody = xml.documentElement.firstChild
        return succeed(soapbody)

    def _twistedSendRequest(self, o):
        """ send a request for object o, return deferred to be called with result as soapbody
        instance
        """
        from twisted.internet import reactor
        deferred = Deferred()
        reactor.connectTCP(host=self._req._host, port=self._req._port,
            factory=self.SoapRequestFactory(con=self, tosend=self._req.make(o), deferred=deferred))
        return deferred

    # Reflection api - getMethods, getModules

    def getModules(self):
        """ get the modules list by parsing the http page for the broker -
        probably there is another way, but who cares?! 8)
        """
        x = minidom.parse(urllib2.urlopen(self._url))
        modulesroot = x.firstChild.nextSibling.firstChild.firstChild.firstChild.nextSibling.nextSibling
        modules = [y.firstChild.firstChild.nodeValue for y in modulesroot.childNodes[1:-1:2]]
        return modules

    def getModule(self, modname):
        if modname == 'ALMotion':
            # specializations
            return ALMotionExtended(self)
        return NaoQiModule(self, modname)

    def makeHelp(self):
        for m in self._modules:
            m.makeHelp()

    # Helpers

    def call(self, modname, meth, *args):
        """ debugging helper call method. In general better to use
            self.module_name.method_name(*args)
        """
        return self._sendRequest(callNaoQiObject(modname, meth, *args))


##################################################################
#
# **Top Level Object**
#
# Higher level functions on connection object are here.
# Lower level are in BaseNaoQiConnection

class NaoQiConnection(BaseNaoQiConnection):

    def __init__(self, url=WEBOTS_LOCALHOST_URL, verbose=True, options=None):
        super(NaoQiConnection, self).__init__(url=url, verbose=verbose,
                options=options)
        self._getInfoObject = getInfoObject('NaoQi')
        self._getBrokerInfoObject = getBrokerInfoObject()
        self._brokername = "soaptest"
        self._camera_module = 'NaoCam' # seems to be a constant. Also, despite having two cameras, only one is operational at any time - so I expect it is like this.
        self._camera_name = 'mysoap_GVM' # TODO: actually this is GVM, or maybe another TLA, depending on Remote/Local? can I do local with python?
        self._registered_to_camera = False
        # raw string (length/meaning depends on colorspace, resolution), width, height
        self._camera_raw_frame = (None, 0, 0)
        self._camera_missed_frames = 0

    def getBrokerInfo(self):
        def onResponse(self, soapbody):
            return getpairs(soapbody.firstChild.firstChild)
        self._sendRequest(self._getBrokerInfoObject).addCallback(onResponse)

    def getInfo(self, modulename):
        def onResponse(soapbody):
            return getpairs(soapbody.firstChild)
        self._getInfoObject.body['albroker:getInfo']['albroker:pModuleName']._children[0] = modulename
        return self._sendRequest(self._getInfoObject).addCallback(onResponse)

    def registerBroker(self, cb = None):
        """
        this registers ourselves as a broker - this is of course not enough, we need to
        to actually listen to this port
        """
        def onResponse(soapbody):
            if cb:
                cb(soapbody.firstChild.firstChild.firstChild.nodeValue)
        obj = registerBroker(name=self._brokername, ip=self._myip, port=self._myport, processId=os.getpid(), modulePointer=-1, isABroker=True, keepAlive=False, architecture=0)
        return self._sendRequest(obj)

    def exploreToGetModuleByName(self, modulename, cb):
        def onRespnse(soapbody):
            cb(getpairs(soapbody.firstChild.firstChild))
        obj = exploreToGetModuleByNameObject(moduleName=modulename, dontLookIntoBrokerName = self._brokername)
        return self._sendRequest(obj, cb)

    def registerToCamera(self,
            resolution=vision_definitions.kQVGA,
            colorspace=vision_definitions.kYUV422InterlacedColorSpace,
            fps=15):
        """ Default parameters are exactly what nao-man (northern bites) use:
        YUV422 color space, 320x240 (Quarter VGA), and 15 fps
        """
        if self._registered_to_camera:
            return succeed(self._camera_name)
        self._camera_resolution = resolution
        self._camera_colorspace = colorspace
        d = self.NaoCam.register(self._camera_name, resolution, colorspace, fps)
        d.addCallback(self._onRegisterToCamera)
        return d

    def _onRegisterToCamera(self, camera_name):
        print "registered to camera under name: %s" % camera_name
        self._camera_name = camera_name
        vd = vision_definitions
        self._camera_param_dimensions_d = {vd.kQVGA:(320, 240)} # TODO - fill it
        self._camera_param_length_factor_d = {vd.kYUV422InterlacedColorSpace: 2}
        width, height = self._camera_param_dimensions_d[self._camera_resolution]
        length = self._camera_param_length_factor_d[self._camera_colorspace] * width * height
        self._camera_param = (width, height, length)
        self._registered_to_camera = True
        return self._camera_name

    def has_imops(self):
        import ctypes
        try:
            imops = ctypes.CDLL('imops.so')
        except:
            print "missing imops (you might want to add burst/lib to LD_LIBRARY_PATH"
            return None
        return imops

    def get_imops(self):
        if hasattr(self, '_image_convertion'):
            return self._image_convertion
            self._image_convertion = (None, None)
            return
        width, height, length = self._camera_param
        imops = self.has_imops()
        if not imops:
            return None
        self._image_convertion = (imops, ' '*(length*3/2))
        return self._image_convertion

    def retrieveImages(self):
        """ Debugging helper - you need to run pynaoqi with the -gthread argument
        for this to work """
        
        import gtk, gobject

        self.registerToCamera()
        w = gtk.Window()
        gtkim = gtk.Image()
        w.add(gtkim)
        w.show_all()

        def getNew():
            width, height, rgb = self.getRGBRemoteFromYUV422()
            pixbuf = gtk.gdk.pixbuf_new_from_data(rgb, gtk.gdk.COLORSPACE_RGB, False, 8, width, height, width*3)
            gtkim.set_from_pixbuf(pixbuf)
            return True
        
        gobject.timeout_add(500, getNew)

    def getRGBRemoteFromYUV422(self):
        d = Deferred()
        def onImageRemoteRaw((yuv, width, height)):
            imops, rgb = self.get_imops()
            if not imops:
                d.callback(None) # TODO - errback?
            imops.yuv422_to_rgb888(yuv, rgb, len(yuv), len(rgb))
            d.callback((width, height, rgb))
        self.getImageRemoteRaw().addCallback(onImageRemoteRaw)
        return d

    def getImageRemoteFromYUV422(self):
        d = self.getRGBRemoteFromYUV422()
        if d is None: return None
        d.addCallback(self.imageFromRGB)
        return d

    def getImageRemoteRaw(self):
        def filter_some(result):
            # We silently ignore missing frames - empty results from our request.
            # no idea why this happens. We just return the last frame
            if len(result) > 0:
                (width, height, layers, colorspace, timestamp_secs,
                timestamp_microsec, imageraw) = result
                self._camera_raw_frame = (imageraw, width, height)
            else:
                self._camera_missed_frames += 1
                print "Bad frame %s" % self._camera_missed_frames
            return self._camera_raw_frame
        d = self.NaoCam.getImageRemote(self._camera_name)
        d.addCallback(filter_some)
        return d

    def getImageRemoteFromRGB(self, debug_file_name = None):
        rgb, width, height = self.getImageRemoteRaw()
        return self.imageFromRGB(width, height, rgb, debug_file_name = debug_file_name)

    def imageFromRGB(self, (width, height, rgb), debug_file_name = None):
        image = Image.fromstring('RGB', (width, height), rgb)
        if debug_file_name:
            if debug_file_name[:1] != '/':
                debug_file_name = os.path.join(os.getcwd(), debug_file_name)
            image.save(debug_file_name)
            file_ctime = datetime.datetime.fromtimestamp(os.stat('test.jpg')[stat.ST_CTIME])
            print "saved to %s, %s" % (debug_file_name, str(file_ctime))
            #os.system('xdg-open %s' % debug_file_name)
        return image

    def setCameraParameter(self, param, value):
        ret = self.NaoCam.setParam(int(param), int(value))
        return ret

    def switchToBottomCamera(self):
        self.setCameraParameter(CAMERA_WHICH_PARAM, CAMERA_WHICH_BOTTOM_CAMERA)

    def switchToTopCamera(self):
        self.setCameraParameter(CAMERA_WHICH_PARAM, CAMERA_WHICH_TOP_CAMERA)

#########################################################################
# Main and Tests


def test():
    target_url = 'http://localhost:9560/'
    print X('SOAP-ENV:Envelope')
    print X('SOAP-ENV:Envelope', attrs=namespaces)
    print getInfoBase
    gi2 = getInfoObject('NaoQi')
    print gi2
    assert(str(gi2) == str(getInfoBase))
    req = Requester(target_url)
    print req.make(getInfoObject('NaoQi'))
    con = NaoQiConnection(target_url)
    broker_info = con.getBrokerInfo()
    print broker_info
    d = dict(broker_info)
    print con.getInfo(d['name'])
    print con.registerBroker()
    print con.exploreToGetModuleByName('ALLogger')
    print con.exploreToGetModuleByName('ALMemory')
    print con.exploreToGetModuleByName('NaoCam')

def main():
    import sys
    url = "http://localhost:9560"
    if len(sys.argv) > 1:
        url = sys.argv[-1]
    print "using target = %s" % url
    con = NaoQiConnection(url)
    broker_info = dict(con.getBrokerInfo())
    print con.getInfo(broker_info['name'])
    #print con.registerBroker()
    #print con.exploreToGetModuleByName('NaoCam')
    print con.registerToCamera()
    con.NaoCam.register('test_cam', vision_definitions.kQQVGA, vision_definitions.kRGBColorSpace, 15)


    c = 0
    meths = (lambda: (con.switchToBottomCamera(), con.getImageRemote('top.jpg')),
             lambda: (con.switchToTopCamera(), con.getImageRemote('bottom.jpg')))
    while True:
        meths[c]()
        c = 1 - c

options = None

# helper function - exactly the same as in burst, handle --ip and --port
def getDefaultOptions():
    global options
    if options is not None: return options
    from optparse import OptionParser
    parser = OptionParser()
    true_storers, false_storers, storers = [], [], []

    # Some helper functions for argument parsing
    def collector(opt, col, kw_base, **kw):
        kwjoint = dict(kw_base)
        kwjoint.update(kw)
        parser.add_option(opt, **kwjoint)
        true_storers.append(opt)
    store_true =lambda opt, **kw: collector(opt, true_storers, {'action':'store_true'}, **kw)
    store_false =lambda opt, **kw: collector(opt, false_storers, {'action':'store_false'}, **kw)
    store = lambda opt, **kw: collector(opt, storers, {'action':'store'}, **kw)

    # Optional Arguments
    store('--ip', dest='ip', default='localhost', help='hostname to connect to')
    store('--port', dest='port', default=None,    help='port to connect to')

    store_true('--twisted', dest='twisted', default=True,
            help='use twisted')
    store_false('--notwisted', dest='twisted',
            help='don\'t use twisted')
    store_true('--locon', dest='localization_on_start',
            help='turn localization on')
    store_true('--reportnew', dest='report_new_packet_sizes',
            help='debug - report new packet sizes')
    store_true('--verbosetwisted', dest='verbose_twisted',
            help='debug - show twisted communication')
    store_true('--manhole', dest='use_manhole',
            help='use manhole shell instead of IPython')
    store_true('--nogtk', dest='nogtk',
            help='debug - turn off gtk integration (NOT WORKING)')
    parser.error = lambda msg: None # only way I know to avoid errors when unknown parameters are given
    options, rest = parser.parse_args()
    # TODO: UNBRAIN DEAD THIS
    # The next part is brain dead, but I don't know how to remove *just*
    # the parameters I used with OptionParser.. delegated option parsers anyone?
    todelete = []
    for i, arg in enumerate(sys.argv):
        if arg in storers:
            todelete.extend([i, i+1])
        if arg in true_storers + false_storers:
            todelete.append(i)
    for i in reversed(todelete):
        if i >= len(sys.argv):
            print "bad arguments.. go home"
            raise SystemExit
        del sys.argv[i]
    on_nao = os.path.exists('/opt/naoqi/bin/naoqi') # hope no one else installs this, faster then running uname?
    options.port = options.port or ((options.ip == 'localhost' and not on_nao and 9560) or 9559)
    return options

default_connection = None
def getDefaultConnection(with_twisted=None):
    """ Returns a singleton connection object to the parameters provided on the command
    line, defaulting to localhost webots connection. Suitable for most uses, except
    for writing apps that connect to multiple robots, where you'll want to instantiate
    the NaoQiConnection objects yourself.
    """
    global default_connection
    if default_connection is None:
        options = getDefaultOptions()
        if with_twisted is not None:
            options.twisted = with_twisted
        url = 'http://%s:%s/' % (options.ip, options.port)
        default_connection = NaoQiConnection(url, options=options)
    return default_connection

if __name__ == '__main__':
    main()

