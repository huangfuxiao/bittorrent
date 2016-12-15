import sys
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
from time import gmtime, strftime
from ConnectPeer import PeerConnection, PeerProtocol, Factory
import thread

def disconnect_thread(factory, connector):
	while 1:
		if factory.download_finished[0]:
			print "Disconnecting..."
			# connector.disconnect()
			reactor.stop()
			return
	sleep(10)

def connect_thread(this_factory, peer_list):
	print strftime("%Y-%m-%d %H:%M:%S", gmtime())
	for peer in peer_list:
		hostandport = peer.split(':')
		reactor.connectTCP(hostandport[0], int(hostandport[1]), this_factory)

		# thread.start_new_thread(disconnect_thread, (this_factory, connector, ) )

	reactor.run(installSignalHandlers=False)

def main():
	if len(sys.argv) < 2 :
		print "Illegal USAGE! USAGE : python driver.py <torrent_file> "
		return

	torrent_file = sys.argv[1]
	
	if not os.path.exists(torrent_file):
		print "Torrent File not exist! Quit "
		return

	file_to_write = open("test", "w+")
	this_torrent = Torrent(torrent_file, file_to_write)
	peer_list = this_torrent.get_peer_list()
	print peer_list
	this_factory = Factory(this_torrent)
	thread.start_new_thread(disconnect_thread, (this_factory, "", ) )
	thread.start_new_thread(connect_thread, (this_factory, peer_list, ) )

	while 1: 
		input = raw_input('>')
		cmd = input.split(' ')
		cmd = cmd[0]
		print cmd
		if cmd == 'help' :
			print "Valid commands: info, peers, status, quit"
		elif cmd == 'info':
			print "Torrent file's information: "
			print "        total length (in byte): ", this_torrent.length
			print "        total number of pieces: ", this_torrent.get_num_pieces()
			print "        total number of blocks: ", int(this_torrent.get_total_num_blocks())
		elif cmd == 'peers' :
			print peer_list
		elif cmd == 'status' :
			this_torrent.get_statistics()
		elif cmd == 'quit' :
			exit(1)
		else:
			print "Valid commands: info, peers, status, quit"

if __name__ == "__main__":
	main()