from xml.dom import minidom

from twisted.internet.protocol import Protocol, ClientFactory, ClientCreator
from twisted.internet.defer import Deferred
import twisted.internet.reactor as reactor

import twisted.internet.error

LOG_HEADERS = False
DEBUG = False

class SoapConnectionManager(object):

    def __init__(self, con):
        self._protocols = []
        self.con = con
        if LOG_HEADERS:
            self.con.log = open('headers.txt', 'a+')

    def _makeNewProtocol(self, tosend, deferred):
        ClientCreator(reactor, lambda: SoapProtocol(con=self.con,
            tosend=tosend, deferred=deferred)).connectTCP(host=self.con._req._host, port=self.con._req._port
            ).addCallback(self._newProtocolConnected)
        return deferred

    def _newProtocolConnected(self, protocol):
        self._protocols.append(protocol)
        if DEBUG:
            print "DEBUG: SoapConnectionManager: protocols: %s" % len(self._protocols)

    def sendPacket(self, tosend):
        deferred = Deferred()
        for prot in self._protocols:
            if prot.ready:
                return prot.sendPacket(tosend, deferred)
        # no existing protocol
        self._makeNewProtocol(tosend=tosend, deferred=deferred)
        return deferred

class SoapProtocol(Protocol):

    """ Single Soap connection. Understands keep-alive in response header.
    Can be reused to send multiple packets as long as user tests the soapProtocol.ready
    before calling soapProtocol.sendPacket
    """

    _packet_sizes = set()

    def __init__(self, con, tosend, deferred):
        self._packets = 0
        self._got = []
        self._got_len = 0
        self.deferred = None
        self.tosend = None
        self.con = con
        self.options = con.options
        self.ready = True
        self._makeReadyForNextPacket()
        if tosend:
            self.sendPacket(tosend, deferred)

    def sendPacket(self, tosend, deferred):
        if not self.ready:
            raise Exception("SoapProtocol.sendPacket called while sending/receiving previous packet")
        self._packets += 1
        if DEBUG:
            print "DEBUG: SoapProtocol %s: packets = %s" % (id(self), self._packets)
        self.tosend = tosend
        self.deferred = deferred
        self.ready = False
        if self.connected:
            self._onConnectedAndHaveSomethingToSend()
        return deferred

    def connectionMade(self):
        self._onConnectedAndHaveSomethingToSend()

    def _onConnectedAndHaveSomethingToSend(self):
        if self.options.verbose_twisted:
            print "sending %s" % self.tosend
        self.transport.write(self.tosend)
        if LOG_HEADERS:
            self.con.log.write("WRITTEN\n" + self.tosend[:300]+"\n\n")

    def dataReceivedHeaders(self, data):
        if self.options.verbose_twisted:
            print "YAY DATA", data[:10]
        # at some point we will be done, then we call our deferred
        self._got.append(data)
        self._headers = ''.join(self._got)
        left_bracket_pos = data.find('<')
        if left_bracket_pos == -1: return # still more headers

        self.parseHeaders()
        if LOG_HEADERS:
            self.con.log.write("READ\n" + self._headers)

        self._got = []
        self._got_len = 0
        self.dataReceived = self.dataReceivedContent
        self.dataReceived(data[left_bracket_pos:])

    def parseHeaders(self):
        """ Set various flags from the headers.
        Parsed:

        content length
        keep alive
        """
        self._content_length = self.con.contentLengthFromHeaders(self._headers)
        self._close_connection = self.con.closeSocketFromHeaders(self._headers)

    def _makeReadyForNextPacket(self):
        self._got = []
        self._got_len = 0
        self.dataReceived = self.dataReceivedHeaders
        self.ready = True

    def dataReceivedContent(self, data):
        if self.options.verbose_twisted:
            print "MORE DATA", data[:10]
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
            # lose connection if not keep alive
            if self._close_connection:
                self.transport.loseConnection()
            else:
                # we shall survive to service another request
                self._makeReadyForNextPacket()
        else:
            if data_len not in self._packet_sizes:
                self._packet_sizes.add(data_len)
                if self.options.report_new_packet_sizes:
                    print "YAY NEW PACKET SIZE: %s (got %s/%s)" % (data_len, self._got_len, self._content_length)

class SoapRequestFactory(ClientFactory):
    """ UNUSED
    """
    verbose = False

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
        if not self.verbose: return
        if reason.type != twisted.internet.error.ConnectionDone:
            print "CONNECTION LOST while sending %s, reason %s" % (self.tosend[:10], reason)

    def clientConnectionFailed(self, connector, reason):
        if not self.verbose: return
        print "CONNECTION FAILED", reason


