from time import time
from xml.dom import minidom

from twisted.internet.protocol import Protocol, ClientFactory, ClientCreator
from twisted.internet.defer import Deferred
import twisted.internet.reactor as reactor

import twisted.internet.error

LOG_HEADERS = False

class SoapConnectionManager(object):

    def __init__(self, con):
        self._protocols = []
        self._errors_connecting = 0
        self.con = con
        self.verbose = con.options.verbose_twisted
        # These two numbers should be equal, difference is roughly a measure of latency / bandwidth
        self._sent = 0
        self._returned = 0
        self._max_protocols = None # NOT IMPLEMENTED YET
        if LOG_HEADERS:
            self.con.log = open('headers.txt', 'a+')

    def _makeNewProtocol(self, tosend):
        deferred = Deferred()
        def makeProtocol():
            return SoapProtocol(con=self.con)
        def sendPacket(protocol):
            if protocol is None:
                return # silently fail - log this? TODO
            protocol.sendPacket(tosend).addCallback(deferred.callback)
        conn_d = ClientCreator(reactor, makeProtocol).connectTCP(
                host=self.con._message_maker._host, port=self.con._message_maker._port)
        conn_d.addCallbacks(self._newProtocolConnected, self._onConnectionError)
        conn_d.addCallback(sendPacket)
        return deferred

    def _newProtocolConnected(self, protocol):
        self._protocols.append(protocol)
        if self.verbose:
            print "DEBUG: SoapConnectionManager: protocols: %s" % len(self._protocols)
        return protocol # for chaining callbacks, always return something useful

    def _onConnectionError(self, error):
        self._errors_connecting += 1
        self._last_connection_error = time()

    def sendPacket(self, tosend):
        """ reuse this method to also clean up closed sockets at the same time.
        note that this is not a solution to why they were closed in the first place. """

        # TODO - rename sendPacket to sendMessage - not actually a single packet
        to_delete = []
        returned = None
        self._sent += 1

        ### Look for existing connection

        for i, prot in enumerate(self._protocols):
            if prot.transport.disconnected:
                to_delete.append(i)
                # TODO - call the callback with an empty response, let it handle it?
                # should probably start using errbacks, perfect for this.
            elif prot.ready and not returned:
                returned = prot.sendPacket(tosend)
                break

        ### Delete timedout connections

        now = time()
        for i in reversed(to_delete):
            if self.verbose:
                print "deleting protocol %s after %s seconds" % (i, now - self._protocols[i]._time_last_send)
            del self._protocols[i]

        ### Create new connection if required

        if not returned:
            # no ready protocol
            if self._max_protocols is not None and len(self._protocols) >= self._max_protocols:
                # queue it
                raise NotImplemented("No Support for Max Protocols yet")
            else:
                # create a new connection
                returned = self._makeNewProtocol(tosend=tosend)

        returned.addCallback(self._logReturnMessage)
        return returned

    def _logReturnMessage(self, ret):
        self._returned += 1
        return ret

class SoapProtocol(Protocol):

    """ Single Soap connection. Understands keep-alive in response header.
    Can be reused to send multiple packets as long as user tests the soapProtocol.ready
    before calling soapProtocol.sendPacket

    Origianlly created just for sending, then receiving. So slightly ugly, but with some
    if's it is now also usable for receive, then send connections (i.e. as a server)
    TODO - refactor properly
    """

    _packet_sizes = set()

    def __init__(self, con):
        self._packets = 0
        self._got = []
        self._got_len = 0
        self.deferred = None
        self.tosend = None
        self.con = con
        self.options = con.options
        self.ready = True
        self.verbose = con.options.verbose_twisted
        self._makeReadyForNextPacket()
        self.connected_deferred = Deferred()

    def sendPacket(self, tosend):
        """ send a single packet, return a deferred that is
        called when a response is available (this is a single connection,
        there is only one outgoing packet)
        """
        if not self.ready:
            raise Exception("SoapProtocol.sendPacket called while sending/receiving previous packet")
        self._time_last_send = time()
        self._packets += 1
        if self.verbose:
            print "DEBUG: SoapProtocol %s: packets = %s" % (id(self), self._packets)
        self.tosend = tosend
        self.deferred = Deferred()
        self.ready = False
        if self.connected:
            self._onConnectedAndHaveSomethingToSend()
        return self.deferred

    def connectionMade(self):
        self.connected_deferred.callback(self)
        self._onConnectedAndHaveSomethingToSend()

    def _onConnectedAndHaveSomethingToSend(self):
        if self.tosend:
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
                self.deferred.callback(soapbody) # This might do something, like write
                                        # to the transport, thus doing the server part.
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


