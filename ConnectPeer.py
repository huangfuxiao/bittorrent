from time import time
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor, task, defer
from bitstring import BitArray
from Torrent import Torrent
import constants
import messages

MSG_INTERESTED = ''

class PeerConnection(object):
	def __init__(self, torrent):
		self.pstrlen = chr(19)
		self.pstr = "BitTorrent protocol"
		self.reserved = "\x00\x00\x00\x00\x00\x00\x00\x00"
		self.info_hash = torrent.info_hash
		self.peer_id = torrent.peer_id

	def __str__(self):
		return self.pstrlen+self.pstr+self.reserved+self.info_hash+self.peer_id

class PeerProtocol(Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.peer_has_pieces = BitArray(len(self.factory.torrent.pieces_array))
        self.message_buffer = bytearray()
        self.pending_requests = 0
        self.interested = False
        self.choked = True
        self.message_timeout = time() #mark for sending KeepAlives

    def connectionMade(self):
        print "connection made"
        handshake_msg = str(PeerConnection(self.factory.torrent))
        self.transport.write(str(handshake_msg))
        self.message_timeout = time()

    def dataReceived(self,data):
        self.message_timeout = time()
        msg_to_send = self.handle_received_data(data)
        for i,message in enumerate(msg_to_send):
            if message is not None:
                self.transport.write(str(message))
                self.message_timeout = time()

    def handle_received_data(self,data):
        print "Handle received data gets started here!"
        msg_to_write = []
        if self.message_buffer:
            self.message_buffer.extend(bytearray(data))
        else:
            self.message_buffer = bytearray(data)

        if self.message_buffer[1:20].lower() == "bittorrent protocol":
            print "handshake received"
            msg_rcvd = self.message_buffer[:68]
            print "This is the mesage received: ", msg_rcvd
            self.message_buffer = self.message_buffer[68:]
            print "This is msg to write before append: ", msg_to_write
            # print "This is messages' interested: ", messages.Interested()
            msg_to_write.append(messages.Interested())
            print "This is msg to write after append: ", msg_to_write
            print "This is the length of message buffer: ", len(self.message_buffer)
            self.interested = True
        return msg_to_write

    def connectionLost(self, reason):
        self.factory.protocols.remove(self)

class Factory(ClientFactory):
    def __init__(self, torrent):
        self.protocols = []
        self.torrent = torrent

    def startedConnecting(self,connector):
        print 'Started to connect.'

    def buildProtocol(self,addr):  
        print 'Connected.'
        protocol = PeerProtocol(self)
        self.protocols.append(protocol)
        return protocol

    def clientConnectionLost(self,connector,reason):
        print 'Lost connection. Reason: ', reason
        #reconnect?

    def clientConnectionFailed(self,connector,reason):
        print 'Connection failed. Reason: ', reason

def main():
    this_torrent = Torrent("InPraiseOfIdleness_archive.torrent")
    # print this_torrent
    peer_list = this_torrent.get_peer_list()
    print peer_list
    this_factory = Factory(this_torrent)
    for peer in peer_list:
        hostandport = peer.split(':')
        reactor.connectTCP(hostandport[0], int(hostandport[1]), this_factory)
        # print this_factory.torrent
        # print this_factory.protocols
    reactor.run()


if __name__ == "__main__":
    main()