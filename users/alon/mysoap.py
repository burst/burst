import re
import socket
from xml.dom import minidom

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
getInfoBase = X('SOAP-ENV:Envelope', namespaces,
        [
            X('SOAP-ENV:Body', [],
                [
                    X('albroker:getInfo', [],
                        [
                            X('albroker:pModuleName', [], ['NaoQi'])
                        ])
                ])
        ])

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
    o.body.C(X('albroker:getInfo').C(X('albroker:pModuleName', [], [modname])))
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
                ('architecture', architecture),
                ('ip', ip),
                ('port', port),
                ('processId', processId),
                ('modulePointer', modulePointer),
                ('isABroker', isABroker),
                ('keepAlive', keepAlive)
            ]
        ])
    o.body.C(X('albroker:registerBroker').C(broker))
    return o

#################################################################################################
# Connection (Top Level object)

DEBUG=True

class NaoQiConnection(object):
    def __init__(self, url):
        self._req = Requester(url)
        self._getInfoObject = getInfoObject('NaoQi')
        self._getBrokerInfoObject = getBrokerInfoObject()

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
        body = h[-1] + s.recv(content_length-1)
        if DEBUG:
            print "***     Got:          ***\n%s" % (headers + body)
        xml = minidom.parseString(body)
        soapbody = xml.documentElement.childNodes[0]
        return soapbody

    def getBrokerInfo(self):
        soapbody = self.sendrecv(self._getBrokerInfoObject)
        ret = soapbody.childNodes[0].childNodes[0] # always a wrapper around the return
        return [(x.nodeName, x.childNodes[0].nodeValue) for x in ret.childNodes]

    def getInfo(self, modulename):
        self._getInfoObject.body['albroker:getInfo']['albroker:pModuleName']._children[0] = modulename
        soapbody = self.sendrecv(self._getInfoObject)
        ret = soapbody.childNodes[0] # always a wrapper around the return
        return [(x.nodeName, x.childNodes[0].nodeValue) for x in ret.childNodes]

#################################################################################################

def test():
    print X('SOAP-ENV:Envelope')
    print X('SOAP-ENV:Envelope', attrs=namespaces)
    print getInfoBase
    gi2 = getInfoObject('NaoQi')
    print gi2
    assert(str(gi2) == str(getInfoBase))
    req = Requester('http://nao.local:9559/')
    print req.make(getInfoObject('NaoQi'))
    con = NaoQiConnection('http://nao.local:9559/')
    broker_info = con.getBrokerInfo()
    print broker_info
    d = dict(broker_info)
    print con.getInfo(d['name'])

if __name__ == '__main__':
    test()

