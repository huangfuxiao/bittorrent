from time import time, sleep
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor, task, defer
from bitstring import BitArray
from Torrent import Torrent
from Piece import Block, Piece, FileWriter
import constants
import messages
from message import *
import sys
import os

BLOCK_SIZE = 2**14
PIECE_SIZE = 2**19

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
        msg_to_send = []
        if self.message_buffer:
            self.message_buffer.extend(bytearray(data))
        else:
            self.message_buffer = bytearray(data)

        if self.message_buffer[1:20].lower() == "bittorrent protocol":
            print "handshake received"
            msg_rcvd = self.message_buffer[:68]
            print "This is the mesage received: ", msg_rcvd
            self.message_buffer = self.message_buffer[68:]
            print "This is msg to write before append: ", msg_to_send
            # msg_to_send.append(messages.Interested())
            msg_to_send.append(create_message('INTERESTED', -1, -1, -1, -1))
            print "This is msg to write after append: ", msg_to_send
            self.interested = True
        if len(self.message_buffer) >= 4:
            message_length = bytes_to_number(self.message_buffer[0:4]) + 4
            i = 0
            while len(self.message_buffer) >= message_length:
                length = bytes_to_number(self.message_buffer[0:4]) + 4 
                this_msg = self.message_buffer[:length]
                response = self.get_response_msg(this_msg)
                self.get_next_send_msg(response, msg_to_send, this_msg)
                # msg_to_send.append(self.get_next_send_msg(response))
                # Move to next message
                self.message_buffer = self.message_buffer[length:]
                message_length = bytes_to_number(self.message_buffer[0:4])+4
        return msg_to_send

    def connectionLost(self, reason):
        self.factory.protocols.remove(self)

    def get_response_msg(self, message_buffer):
        msg_list = ['CHOKE', 'UNCHOKE', 'INTERESTED', 'NOTINTERESTED', 'HAVE', 'BITFIELD', 'REQUEST', 'PIECE', 'CANCEL', 'PORT']
        if(len(message_buffer) == 4):
            response_msg = 'KEEPALIVE'
        else:
            id = message_buffer[4]
            if (id>9) | (id<0):
                response_msg = ''
            else:
                response_msg = msg_list[id]
                if (id == 7):
                    msg_length = bytes_to_number(message_buffer[0:4])
                    index = bytes_to_number(message_buffer[5:9])
                    begin = bytes_to_number(message_buffer[9:13])
                    # block = bytes_to_number(message_buffer[13:17])
                    print "Piece index, begin, block, msg_length: ", index, begin, len(message_buffer[13:]), msg_length

        return response_msg

    def get_next_send_msg(self, msg_type, msg_list, message_buffer):
        msg_to_send = ''
        if(msg_type == 'CHOKE'):
            print 'Received message: Choked'
            self.choked = True
        elif(msg_type == 'UNCHOKE'):
            print 'Received message: Unchoke'
            self.choked = False
            total_num_pieces = self.factory.torrent.get_num_pieces()
            total_num_blocks = self.factory.torrent.get_num_blocks()
            # msg_to_send = create_message('REQUEST', 0, 0, 2**14, -1)
            # msg_list.append(msg_to_send)
            i=0
            for piece in range(0, int(total_num_pieces-1)):
            # for piece in range(0, 2):
                offset = 0
                for block in range(0, int(total_num_blocks)):
                    # create_message('REQUEST', piece, offset, 2**14, -1)
                    msg_list.append(create_message('REQUEST', piece, offset, BLOCK_SIZE, -1))
                    offset = offset + 2**14
                    i = i+1
                    sleep(0.1)
                    # print "This is the i's block received: ", i
            last_num_blocks = self.factory.torrent.get_last_num_blocks()
            last_block_length = self.factory.torrent.get_last_block_length()
            piece = total_num_pieces-1
            offset = 0
            for block in range(0, int(last_num_blocks-1)):
                msg_list.append(create_message('REQUEST', piece, offset, BLOCK_SIZE, -1))
                offset = offset + 2**14
                i = i+1
                sleep(0.1)
            msg_list.append(create_message('REQUEST', piece, offset, last_block_length, -1))

            print 'Here are number of pieces, blocks, i: ', total_num_pieces, total_num_blocks, i
            # create_message('REQUEST', 0, 0, 2**14, -1)
            # msg_to_send = create_message('REQUEST')
            # TO BE IMPLEMENTED
            # send_next_request()
        elif(msg_type == 'INTERESTED'):
            print 'Received message: Interested'
        elif(msg_type == 'UNINTERESTED'):
            print 'Received message: Uninterested'
        elif(msg_type == 'HAVE'):
            print 'Received message: Have'
            # TO BE IMPLEMENTED
            
        elif(msg_type == 'BITFIELD'):
            print 'Received message: Bitfield'
            # TO BE IMPLEMENTED
            
        elif(msg_type == 'REQUEST'):
            print 'Received message: Request'
            # TO BE IMPLEMENTED
            
        elif(msg_type == 'PIECE'):
            print 'Received message: Piece'
            # TO BE IMPLEMENTED
            msg_length = bytes_to_number(message_buffer[0:4])
            index = bytes_to_number(message_buffer[5:9])
            begin = bytes_to_number(message_buffer[9:13])

            
        elif(msg_type == 'CANCEL'):
            print 'Received message: Cancel'
            
        elif(msg_type == 'PORT'):
            print 'Received message: Port'
            
        return msg_to_send

        
        

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
    print this_torrent.get_num_pieces()
    print this_torrent.get_num_blocks()
    print this_torrent.get_last_num_blocks()
    print this_torrent.get_last_block_length()
    peer_list = this_torrent.get_peer_list()
    print peer_list
    this_factory = Factory(this_torrent)

    if os.path.exists("test.txt"):
        file_to_write = open("test.txt", "rb+")
    else:
        file_to_write = open("test.txt", "w+")
    f = open("test.txt", "r+")

    file_to_write = FileWriter(this_torrent.length, file_to_write, this_torrent.pieces_array)
    # for peer in peer_list:
    #     hostandport = peer.split(':')
    #     reactor.connectTCP(hostandport[0], int(hostandport[1]), this_factory)
    #     # print this_factory.torrent
    #     # print this_factory.protocols
    # reactor.run()


if __name__ == "__main__":
    main()