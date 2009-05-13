from xml.dom import minidom

from twisted.internet.protocol import Protocol, ClientFactory
import twisted.internet.error

class SoapProtocol(Protocol):

    _packet_sizes = set()

    def __init__(self, con, tosend, deferred):
        self._got = []
        self._got_len = 0
        self.deferred = deferred
        self.tosend = tosend
        self.con = con

    def connectionMade(self):
        #print "sending %s" % tosend
        self.transport.write(self.tosend)

    def dataReceivedHeaders(self, data):
        #print "YAY DATA", data[:10]
        # at some point we will be done, then we call our deferred
        self._got.append(data)
        self._headers = ''.join(self._got)
        left_bracket_pos = data.find('<')
        if left_bracket_pos == -1: return # still more headers
        self._content_length = self.con.contentLengthFromHeaders(self._headers)

        self._got = []
        self._got_len = 0
        self.dataReceived = self.dataReceivedContent
        self.dataReceived(data[left_bracket_pos:])

    def dataReceivedContent(self, data):
        data_len = len(data)
        self._got_len += data_len
        self._got.append(data)
        if self._got_len >= self._content_length:
            body = ''.join(self._got)
            xml = minidom.parseString(body)
            soapbody = xml.documentElement.firstChild
            # we filter out fault codes for now, just print them out
            # maybe add a cb for that later? (user settable) (or use errback mechanism)
            if soapbody.firstChild.nodeName == 'SOAP-ENV:Fault':
                print "Got a fault:\n%s" % soapbody.firstChild.toprettyxml()
            else:
                self.deferred.callback(soapbody)
            self.transport.loseConnection()
        else:
            if data_len not in self._packet_sizes:
                self._packet_sizes.add(data_len)
                print "YAY NEW PACKET SIZE: %s (got %s/%s)" % (data_len, self._got_len, self._content_length)

    dataReceived = dataReceivedHeaders

class SoapRequestFactory(ClientFactory):

    def __init__(self, con, tosend, deferred):
        #super(ClientFactory, self).__init__() # doesn't work, classobj, besides no ClientFactory.__init__
        self.tosend = tosend
        self.deferred = deferred
        self.con = con
    
    def startedConnecting(self, connector):
        #print "YAY CONNECTING", connector
        pass

    def buildProtocol(self, addr):
        return SoapProtocol(con=self.con, tosend=self.tosend, deferred=self.deferred)

    def clientConnectionLost(self, connector, reason):
        if reason.type != twisted.internet.error.ConnectionDone:
            print "CONNECTION LOST", reason

    def clientConnectionFailed(self, connector, reason):
        print "CONNECTION FAILED", reason


