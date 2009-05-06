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

import vision_definitions # copied from $AL_DIR/extern/python/vision_definisions.py
if DEBUG:
    import memory

#########################################################################
# Constants

CAMERA_WHICH_PARAM = 18
CAMERA_WHICH_BOTTOM_CAMERA = 1
CAMERA_WHICH_TOP_CAMERA = 0

# ALMotion.gotoBodyAngles
INTERPOLATION_LINEAR = 0
INTERPOLATION_SMOOTH = 1

#########################################################################
# Utilities

def getip():
    return [x for x in re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', os.popen('ifconfig').read()) if x[:3] != '255' and x != '127.0.0.1' and x[-3:] != '255'][0]

def compresstoprint(s, first, last):
    if len(s) < first + last + 3:
        return s
    return s[:first] + '\n...\n' + s[-last:]

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
        if isinstance(x, int):
            thetype = 'xsd:int'
        elif isinstance(x, float):
            thetype = 'xsd:float'
        elif isinstance(x, bool):
            thetype = 'xsd:boolean'
        else:
            thetype = 'xsd:string'
        x = str(x)
        children = [x]
    return X('item', [('xsi:type', thetype)], children)

def callNaoQiObject(mod, meth, *args):
    """ Call a method. Returns the xml
    object, you need to actually use it, with con.sendrecv
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

##################################################################
# NaoQiModule, NaoQiMethod (Top Level objects)

class NaoQiParam(object):
    
    def __init__(self, ztype, zname, zdoc):
        ztype = int(ztype)
        self.__doc__ = zdoc
        self._type = nao_type_to_py_type.get(ztype, ztype)
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
nao_type_to_py_type = {
    1: None, # void
    2: bool,
    3: int,
    4: float,
    5: str,
    6: ARRAY,
    24: ARRAY,
    25: VECTOR_STRING,
    }

def arrayctor(node):
    return [get_xsi_type_to_ctor(x.attributes['xsi:type'].value)(x) for x in node.firstChild.childNodes]

xsi_type_to_ctor = {
    'xsd:int': lambda x: int(x.firstChild.nodeValue),
    'xsd:float': lambda x: float(x.firstChild.nodeValue),
    'xsd:string': lambda x: str(x.firstChild.nodeValue),
    'xsd:boolean': lambda x: str(x.firstChild.nodeValue) != 'false',
    'xsd:base64Binary': lambda x: base64.decodestring(x.firstChild.nodeValue),
    'nil': lambda x: str(x.firstChild.nodeValue),
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
        self._rettype = nao_type_to_py_type.get(rettype, rettype)
        self.__doc__ = doc
        self._name = name

    def __str__(self):
        return str(self._rettype)

    def __repr__(self):
        return '<NQRet %s>' % str(self._rettype)

    def fromNaoQiCall(self, obj):
        # TODO - check error
        ret = obj.firstChild.firstChild
        if self._rettype == None:
            return None
        if self._rettype in set([bool, int, float, str]):
            return self._rettype(ret.firstChild.firstChild.nodeValue)
        if self._rettype in [ARRAY, VECTOR_STRING]:
            if ret.firstChild is None:
                return []
            return [get_xsi_type_to_ctor(x.attributes['xsi:type'].value)(x) for x in ret.firstChild.childNodes]
        return ret

##################################################################

class NaoQiMethod(object):

    def __init__(self, mod, name):
        self._mod = mod
        self._con = mod._con
        self._name = name
        self._hasdocs = False
        self.__doc__ = 'call con.%s.%s.makeHelp() to get real help.' % (self._mod._modname, self._name)

    def makeHelp(self):
        if self._hasdocs:
            return
        self._getDocs()
        self._hasdocs = True

    def _getDocs(self):
        """ when first time someone accesses the doc of the method we go and get it
        also for the "hidden" parameters _params and _return """
        doc = self.getMethodHelp().firstChild.firstChild.firstChild
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

    def _getDocParam(self):
        self._getDocs()
        return self._param

    def _getDocReturn(self):
        self._getDocs()
        return self._return

    def _getDocDoc(self):
        self._getDocs()
        return self.__doc__

    def getMethodHelp(self):
        return self._con.sendrecv(callNaoQiObject(self._mod._modname, 'getMethodHelp', self._name))

    def __call__(self, *args):
        if not self._hasdocs:
            print "going to get help..",
            self.makeHelp()
            print "done"
        if len(args) != len(self._params):
            raise Exception("Wrong number of parameters: expected %s, got %s" % (len(self._params), len(args)))
        for i, (p, a) in enumerate(zip(self._params, args)):
            if not p.validate(a):
                raise Exception("Argument %s for %s is bad: type is %s, given value is %s" % (i, self._name, p, a))
        return self._return.fromNaoQiCall(self._con.sendrecv(callNaoQiObject(self._mod._modname, self._name, *args)))

##################################################################

class ModulesHolder(object):
    pass

class MethodHolder(object):
    pass

##################################################################

class NaoQiModule(object):
    def __init__(self, con, modname):
        self._con = con
        self._modname = modname
        # async? nah, don't bother right now. (everything here
        # should be twisted.. ok, it can be asynced some other way)
        self.methods = MethodHolder()
        self.method_names = self.getMethods()
        for meth in self.method_names:
            methobj = NaoQiMethod(self, meth)
            setattr(self, meth, methobj)
            setattr(self.methods, meth, methobj)
        # this actually uses one of the methods above!
        self._hasdocs = False
        self.__doc__ = """ Call con.%s.makeHelp() to generate help for this module and it's methods """ % self._modname

    def makeHelp(self):
        print "going to get help..",
        self._getDoc()
        for meth in self.methods.__dict__.values():
            if hasattr(meth, 'makeHelp'):
                meth.makeHelp()
        print "done"
        self._hasdocs = True

    def _getDoc(self):
        """ self annihilating method """
        self.__doc__ = self.moduleHelp()[0]
        return self.__doc__

    def getName(self):
        return self._modname

    def getMethods(self):
        """ returns the method names in unicode for the given module
        """
        result = self._con.sendrecv(callNaoQiObject(self._modname,
                'getMethodList'))
        return [e.firstChild.wholeText for e in result.firstChild.firstChild.firstChild.childNodes]

    def justModuleHelp(self):
        return self._con.sendrecv(callNaoQiObject(self._mod._modname, 'moduleHelp'))

DEG_TO_RAD = math.pi/180.0

class ALMotionExtended(NaoQiModule):

    def __init__(self, con):
        NaoQiModule.__init__(self, con, 'ALMotion')

    def executeMove(self, moves):
        """ Work like northern bites code:
        interpolation - TODO
        """
        for move in moves:
            larm, lleg, rleg, rarm, interp_time, interp_type = move
            curangles = self.getBodyAngles()
            joints = curangles[:2] + [x*DEG_TO_RAD for x in list(larm) + [0.0, 0.0] +
                                        list(lleg) + list(rleg) + list(rarm) + [0.0, 0.0]]
            self.gotoBodyAngles(joints, interp_time, interp_type)
        
##################################################################
# Connection (Top Level object)

def getpairs(elem):
    """ helper method for parsing DOM Elements's """
    return [(x.nodeName, x.firstChild.nodeValue) for x in elem.childNodes]

class NaoQiConnection(object):

    def __init__(self, url="http://localhost:9560/", verbose = True):
        self.verbose = True
        self._url = url
        self._req = Requester(url)
        self._getInfoObject = getInfoObject('NaoQi')
        self._getBrokerInfoObject = getBrokerInfoObject()
        self._myip = getip()
        self._myport = 12345 # bogus - we are acting as a broker - this needs to be a seperate class
        self._brokername = "soaptest"
        self._camera_module = 'NaoCam' # seems to be a constant. Also, despite having two cameras, only one is operational at any time - so I expect it is like this.
        self._camera_name = 'mysoap_GVM' # TODO: actually this is GVM, or maybe another TLA, depending on Remote/Local? can I do local with python?
        
        self._modules = []
        for i, modname in enumerate(self.getModules()):
            if self.verbose:
                print "(%s) %s.." % (i + 1, modname),
                sys.stdout.flush()
            mod = self.getModule(modname)
            self._modules.append(mod)
        if self.verbose: print
        self.modules = ModulesHolder()
        for m in self._modules:
            self.__dict__[m.getName()] = m
            self.modules.__dict__[m.getName()] = m

    def sendrecv(self, o):
        s = socket.socket()
        s.connect((self._req._host, self._req._port))
        tosend = self._req.make(o)
        if DEBUG:
            print "***     Sending:     ***\n%s" % tosend
        s.send(tosend)
        # get headers, read size, read the rest
        h = []
        c = None
        while c != '<':
            c = s.recv(1)
            h.append(c)
        headers = ''.join(h[:-1])
        content_length = int(re.search('Content-Length: ([0-9]+)', headers).groups()[0])
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
        xml = minidom.parseString(body)
        soapbody = xml.documentElement.firstChild
        return soapbody

    def getBrokerInfo(self):
        soapbody = self.sendrecv(self._getBrokerInfoObject)
        return getpairs(soapbody.firstChild.firstChild)

    def getInfo(self, modulename):
        self._getInfoObject.body['albroker:getInfo']['albroker:pModuleName']._children[0] = modulename
        soapbody = self.sendrecv(self._getInfoObject)
        return getpairs(soapbody.firstChild)

    def registerBroker(self):
        """
        this registers ourselves as a broker - this is of course not enough, we need to
        to actually listen to this port
        """
        obj = registerBroker(name=self._brokername, ip=self._myip, port=self._myport, processId=os.getpid(), modulePointer=-1, isABroker=True, keepAlive=False, architecture=0)
        soapbody = self.sendrecv(obj)
        return soapbody.firstChild.firstChild.firstChild.nodeValue

    def exploreToGetModuleByName(self, modulename):
        obj = exploreToGetModuleByNameObject(moduleName=modulename, dontLookIntoBrokerName = self._brokername)
        soapbody = self.sendrecv(obj)
        return getpairs(soapbody.firstChild.firstChild)

    def registerToCamera(self,
            resolution=vision_definitions.kQQVGA,
            colorspace=vision_definitions.kRGBColorSpace,
            fps=15):
        self._camera_name = self.NaoCam.register(self._camera_name, resolution, colorspace, fps)
        return self._camera_name

    def getImageRemoteRGB(self):
        """
    <albroker:meth>getImageRemote</albroker:meth><albroker:p><item xsi:type="Array"><item xsi:type="xsd:string">testvision_GVM</item></item></albroker:p>
        """
        (width, height, layers, colorspace, timestamp_secs, timestamp_microsec,
            imageraw) = self.NaoCam.getImageRemote(self._camera_name)
        return imageraw, width, height

    def getImageRemote(self, debug_file_name = None):
        imageraw, width, height = self.getImageRemoteRGB()
        image = Image.fromstring('RGB', (width, height), imageraw)
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

    # Reflection api - getMethods, getModules

    def getModules(self):
        """ get the modules list by parsing the http page for the broker -
        probably there is another way, but who cares?! 8)
        """
        if self.verbose:
            print "retrieving modules..",
        x = minidom.parse(urllib2.urlopen(self._url))
        modulesroot = x.firstChild.nextSibling.firstChild.firstChild.firstChild.nextSibling.nextSibling
        modules = [y.firstChild.firstChild.nodeValue for y in modulesroot.childNodes[1:-1:2]]
        if self.verbose:
            print "%s" % len(modules)
        return modules

    def getModule(self, modname):
        if modname == 'ALMotion':
            # specializations
            return ALMotionExtended(self)
        return NaoQiModule(self, modname)

    # Helpers

    def call(self, modname, meth, *args):
        """ debugging helper call method. In general better to use
            self.module_name.method_name(*args)
        """
        return self.sendrecv(callNaoQiObject(modname, meth, *args))

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

def asaf():
    sys.path.append('/home/asaf/src/nao-man/motion')
    import SweeterMoves
    globals()['SweeterMoves'] = SweeterMoves
    globals()['con'] = NaoQiConnection('http://maldini:9559')    

# helper function - exactly the same as in burst, handle --ip and --port
def getDefaultOptions():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--ip', action='store', dest='ip', default='localhost')
    parser.add_option('--port', action='store', dest='port', default=None)
    options, rest = parser.parse_args()
    options.port = options.port or ((options.ip == 'localhost' and 9560) or 9559) 
    return options

if __name__ == '__main__':
    main()

