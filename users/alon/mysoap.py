import re
import os
import socket
import base64 # for getRemoteImage
from xml.dom import minidom
from time import sleep
import stat
import datetime

import Image

import vision_definitions # copied from $AL_DIR/extern/python/vision_definisions.py
import memory

#################################################################################################
# Constants

CAMERA_WHICH_PARAM = 18
CAMERA_WHICH_BOTTOM_CAMERA = 1
CAMERA_WHICH_TOP_CAMERA = 0

#################################################################################################
# Utilities

def getip():
    return [x for x in re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', os.popen('ifconfig').read()) if x[:3] != '255' and x != '127.0.0.1' and x[-3:] != '255'][0]

def compresstoprint(s, first, last):
    if len(s) < first + last + 3:
        return s
    return s[:first] + '\n...\n' + s[-last:]

#################################################################################################
# totally minimal SOAP Implementation

class XMLObject(object):

    def __init__(self, name, attrs=[], children=[]):
        self._name = name
        self._attrs = list(attrs)
        self._children = list(children)
        self._d = {}
        for c in self._children:
            if type(c) is str: continue
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

#################################################################################################
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
        else:
            thetype = 'xsd:string'
        x = str(x)
        children = [x]
    return X('item', [('xsi:type', thetype)], children)

def callNaoQiObject(mod, meth, *args):
    """<albroker:callNaoqi>
    <albroker:mod>NaoCam</albroker:mod>
    <albroker:meth>register</albroker:meth>
    <albroker:p>
        <item xsi:type="Array">
            <item xsi:type="xsd:string">testvision_GVM</item>
            <item xsi:type="xsd:int">2</item>
            <item xsi:type="xsd:int">11</item>
            <item xsi:type="xsd:int">15</item>
        </item>
    </albroker:p></albroker:callNaoqi>
    """
    o = S()
    p = serializeToSoap(args) # note - this always creates an Array arround them
    o.body.C(X('albroker:callNaoqi', children=[
        X('albroker:mod', [], [mod]),
        X('albroker:meth', [], [meth]),
        X('albroker:p', [], [p])]))
    return o

##########################################################################################
# Connection (Top Level object)

DEBUG=False

class NaoQiConnection(object):
    def __init__(self, url):
        self._req = Requester(url)
        self._getInfoObject = getInfoObject('NaoQi')
        self._getBrokerInfoObject = getBrokerInfoObject()
        self._myip = getip()
        self._myport = 12345 # bogus - we are acting as a broker - this needs to be a seperate class
        self._brokername = "soaptest"
        self._camera_module = 'NaoCam' # seems to be a constant. Also, despite having two cameras, only one is operational at any time - so I expect it is like this.
        self._camera_name = 'mysoap_GVM' # TODO: actually this is GVM, or maybe another TLA, depending on Remote/Local? can I do local with python?

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
        print "memory = %s" % memory.memory()
        body = h[-1] + ''.join(rest)
        if DEBUG:
            print "***     Got:          ***\n%s" % compresstoprint(headers + body, 1000, 1000)
            print "*************************"
        xml = minidom.parseString(body)
        soapbody = xml.documentElement.childNodes[0]
        return soapbody

    def getBrokerInfo(self):
        soapbody = self.sendrecv(self._getBrokerInfoObject)
        return self.getpairs(soapbody.childNodes[0].childNodes[0])

    def getInfo(self, modulename):
        self._getInfoObject.body['albroker:getInfo']['albroker:pModuleName']._children[0] = modulename
        soapbody = self.sendrecv(self._getInfoObject)
        return self.getpairs(soapbody.childNodes[0])

    def getpairs(self, elem):
        return [(x.nodeName, x.childNodes[0].nodeValue) for x in elem.childNodes]

    def getitems(self, elem):
        # like getpairs, but ignore the names - they will all be "item"
        return [x.childNodes[0].nodeValue for x in elem.childNodes]

    def registerBroker(self):
        """
        this registers ourselves as a broker - this is of course not enough, we need to
        to actually listen to this port
        """
        obj = registerBroker(name=self._brokername, ip=self._myip, port=self._myport, processId=os.getpid(), modulePointer=-1, isABroker=True, keepAlive=False, architecture=0)
        soapbody = self.sendrecv(obj)
        return soapbody.childNodes[0].childNodes[0].childNodes[0].nodeValue

    def exploreToGetModuleByName(self, modulename):
        obj = exploreToGetModuleByNameObject(moduleName=modulename, dontLookIntoBrokerName = self._brokername)
        soapbody = self.sendrecv(obj)
        return self.getpairs(soapbody.childNodes[0].childNodes[0])

    def registerToCamera(self,
            resolution=vision_definitions.kQQVGA,
            colorspace=vision_definitions.kRGBColorSpace,
            fps=15):
        obj = callNaoQiObject(self._camera_module, 'register', self._camera_name, resolution, colorspace, fps)
        soapbody = self.sendrecv(obj)
        # return value is a single string, the name to use for all further communication
        self._camera_name = soapbody.childNodes[0].childNodes[0].childNodes[0].childNodes[0].nodeValue
        return self._camera_name

    def getImageRemoteRGB(self):
        """
    <albroker:meth>getImageRemote</albroker:meth><albroker:p><item xsi:type="Array"><item xsi:type="xsd:string">testvision_GVM</item></item></albroker:p>
        """
        obj = callNaoQiObject(self._camera_module, 'getImageRemote', self._camera_name)
        soapbody = self.sendrecv(obj)
        (width, height, layers, colorspace, timestamp_secs, timestamp_microsec,
            encoded_image) = self.getitems(soapbody.childNodes[0].childNodes[0].childNodes[0])
        width, height = int(width), int(height)
        imageraw = base64.decodestring(encoded_image)
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
        obj = callNaoQiObject(self._camera_module, 'setParam', int(param), int(value))
        soapbody = self.sendrecv(obj)
        return self.getitems(soapbody.childNodes[0].childNodes[0])

    def switchToBottomCamera(self):
        self.setCameraParameter(CAMERA_WHICH_PARAM, CAMERA_WHICH_BOTTOM_CAMERA)

    def switchToTopCamera(self):
        self.setCameraParameter(CAMERA_WHICH_PARAM, CAMERA_WHICH_TOP_CAMERA)

#################################################################################################
# Main and Tests

target_url = 'http://messi.local:9559/'

def test():
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
    url = target_url
    if len(sys.argv) > 1:
        url = sys.argv[-1]
    print "using target = %s" % url
    con = NaoQiConnection(url)
    broker_info = dict(con.getBrokerInfo())
    print con.getInfo(broker_info['name'])
    print con.registerBroker()
    print con.exploreToGetModuleByName('NaoCam')
    print con.registerToCamera()

    c = 0
    meths = (lambda: (con.switchToBottomCamera(), con.getImageRemote('top.jpg')),
             lambda: (con.switchToTopCamera(), con.getImageRemote('bottom.jpg')))
    while True:
        meths[c]()
        c = 1 - c

if __name__ == '__main__':
    main()

