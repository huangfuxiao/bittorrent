from bencode import bencode, bdecode
import hashlib
import requests
import string
import random

PEER_ID_INIT = '-UT1000-'
LOCAL_PORT = 6888

Class Torrent(object):
	def __init__(self, file_name):
		metainfo = self.get_metainfo(file_name)
		self.info = metainfo['info']
		self.announce = metainfo['announce']
		self.comment = metainfo['comment']
		sha_info = hashlib.sha1(bencode(self.info))
		self.info_hash = sha_info.digest()
		self.peer_id = self.generate_peer_id()
		self.length = self.get_total_length()
		
		self.piece_length = self.info['piece length']
		self.uploaded = 0
		self.download = 0
		self.left = self.length
		self.no_peer_id = 0
		self.event = "started"
		self.port = LOCAL_PORT
		self.param_dict = {'info_hash':self.info_hash, 'peer_id':self.peer_id, 'port':self.port,
                           'uploaded':self.uploaded,'downloaded':self.downloaded, 'left':self.left, 
                           'compact':self.compact, 'no_peer_id':self.no_peer_id, 'event':self.event}

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

    def get_peer_list(self)
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
    		else i%6 == 5:
    			port = port + ord(c)
    			peer_addr +=':' + str(port)
    			peer_list.append(peer_addr)
    			peer_addr = ''
    			port = 0
    	return peer_list

    def main():
    	this_torrent = Torrent("test.torrent")
    	peer_list = this_torrent.get_peer_list()
    	print this_torrent

