from bencode import bencode, bdecode
import hashlib
import requests
import string
import random
import os
import math
from Piece import Block, Piece, FileWriter
from os import path, mkdir
from time import gmtime, strftime

PEER_ID_INIT = '-UT1000-'
LOCAL_PORT = 6888
BLOCK_SIZE = 2**14
PIECE_SIZE = 2**19

class Torrent(object):
	def __init__(self, file_name, file_to_write):
		metainfo = self.get_metainfo(file_name)
		self.info = metainfo['info']
		self.announce = metainfo['announce']
		self.comment = metainfo['comment']
		sha_info = hashlib.sha1(bencode(self.info))
		self.info_hash = sha_info.digest()
		self.peer_id = self.generate_peer_id()
		self.length = self.get_total_length()
		self.compact = 1
		self.piece_length = self.info['piece length']
		self.uploaded = 0
		self.download = 0
		self.left = self.length
		self.no_peer_id = 0
		self.event = "started"
		self.port = LOCAL_PORT
		self.param_dict = {'info_hash':self.info_hash, 'peer_id':self.peer_id, 'port':self.port,
							'uploaded':self.uploaded,'downloaded':self.download, 'left':self.left, 
							'compact':self.compact, 'no_peer_id':self.no_peer_id, 'event':self.event}
		pieces = self.info['pieces']
		self.pieces_array = []
		total_pieces = 0
		while len(pieces) > 0:
			self.pieces_array.append(pieces[0:20])
			pieces = pieces[20:]
			total_pieces = total_pieces + 1
		self.total_pieces = total_pieces
		self.file_to_write = FileWriter(self.length, file_to_write, self.pieces_array)
		if 'name' in self.info:
			self.folder_name = self.info['name']
		else:
			self.folder_name = 'download'

	def __str__(self):
		return "Torrent: announce %s \nlength %d\comment %s\ninfo_hash:%s\n" % (self.announce, self.length, self.comment, self.info_hash)

	def get_metainfo(self, file_name):
		f = open(file_name, 'r')
		metainfo = bdecode(f.read())
		f.close()
		return metainfo

	def generate_peer_id(self):
		N = 20 - len(PEER_ID_INIT)
		end = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(N))
		peer_id = PEER_ID_INIT + end
		return peer_id

	def get_total_length(self):
		length = 0
		if 'length' in self.info:
			length = self.info['length']
		else:
			for file in self.info['files']:
				length += file['length']
		return length

	def send_tracker_request(self):
		r = requests.get(self.announce, params=self.param_dict)
		return r

	def get_peer_list(self):
		peer_list = []
		r = self.send_tracker_request()
		response = bdecode(r.content)
		peers = response['peers']
		peer_addr = ''
		port = 0
		for i,c in enumerate(peers):
			if i%6 <= 2:
				peer_addr += str(ord(c))+'.'
			elif i%6 == 3:
				peer_addr += str(ord(c))
			elif i%6 == 4:
				port = ord(c)*256
			elif i%6 == 5:
				port = port + ord(c)
				peer_addr +=':' + str(port)
				peer_list.append(peer_addr)
				peer_addr = ''
				port = 0
		return peer_list

	def get_num_pieces(self):
		return len(self.pieces_array)

	def get_num_blocks(self):
		num_blocks = self.piece_length/BLOCK_SIZE
		if self.piece_length % BLOCK_SIZE != 0:
			num_blocks = num_blocks+1
		return num_blocks

	def get_last_num_blocks(self):
		last_piece_length = self.length % PIECE_SIZE
		num_blocks_last = math.ceil(float(last_piece_length)/BLOCK_SIZE)
		return int(num_blocks_last)

	def get_last_block_length(self):
		# print self.length
		last_piece_length = self.length % PIECE_SIZE
		last_block_length = last_piece_length % BLOCK_SIZE
		return int(last_block_length)

	def get_total_num_blocks(self):
		total_pieces = len(self.pieces_array)
		last_piece_length = self.length % PIECE_SIZE
		num_blocks_last = math.ceil(float(last_piece_length)/BLOCK_SIZE)
		total_blocks = (total_pieces-1)*32 + num_blocks_last
		return total_blocks
	
	def write_single_file(self):
		print "Download a single file"
		extension = self.folder_name.rsplit('.',1)[1]
		rename("test", self.folder_name+extension) 

	def write_multiple_files(self):
		print 'Download multiple files.'
		folder_path = os.path.dirname(__file__)
		folder_path = path.join(folder_path, self.folder_name)
		if not path.exists(folder_path):
			mkdir(folder_path)
		f_read = open("test",'rb')		
		for element in self.info['files']:
			path_list = element['path']
			i = 0
			sub_folder = folder_path
			while i + 1 < len(path_list):  #create directory structure
				sub_folder = path.join(sub_folder, path_list[i])
				if not path.isdir(sub_folder): #folder does not exist yet
					mkdir(sub_folder)
				i += 1
			final_file_path = path.join(sub_folder, path_list[-1])
			f_write = open(final_file_path, 'wb')
			f_write.write(f_read.read(element['length']))
			#cleanup:
			f_write.close()
		f_read.close()
		os.remove("test")
		print 'Write multiple files finished.'
		print strftime("%Y-%m-%d %H:%M:%S", gmtime())

	def write_to_file(self):
		if 'files' in self.info:
			self.write_multiple_files()
		else:
			self.write_single_file()

	def get_statistics(self):
		file = self.file_to_write
		pieces = file.piece_list
		total_blocks = self.get_total_num_blocks()
		total_blocks_finished = 0
		for piece in range(len(pieces)):
			num_blocks_finished = file.piece_list[piece].bitmap.count()
			total_blocks_finished = total_blocks_finished+num_blocks_finished
		
		if total_blocks_finished<total_blocks:
			bytes_downloaded = total_blocks_finished*BLOCK_SIZE
		else:
			bytes_downloaded = (total_blocks_finished-1)*BLOCK_SIZE+self.get_last_block_length()
		
		print "Number of bytes has been downloaded: ", bytes_downloaded, "/", self.length
		print "Percentage of bytes downloaded:      ", str(float(bytes_downloaded)/self.length*100)+'%'




# def main():
#     this_torrent = Torrent("InPraiseOfIdleness_archive.torrent")
#     print this_torrent
#     peer_list = this_torrent.get_peer_list()
#     print peer_list
#     	# peer_list = this_torrent.get_peer_list()
#     	# print this_torrent
#     	# print peer_list

# if __name__ == "__main__":
#     main()



