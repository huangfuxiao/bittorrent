# BitTorrent
Network Project

Name: Yiwei Pi/ Bingbing Li

Login: ypi1 / bli12

Language: Python


================================================================================================================
                                                 DESIGN
================================================================================================================
## 1. Torrent:

#### Class:
	    Torrent(object):
	    	info 		       
	    	announce      	   
	    	comment            
	    	info_hash 		   
	    	peer_id            
	    	length
	    	compact 
		    piece_length 
		    uploaded 
		    download 
		    left 
		    no_peer_id 
		    event 
		    port 
		    param_dict
		    pieces_array
		    total_pieces
		    file_to_write
		    folder_name

#### Functions:
* get_metainfo(file_name)
* generate_peer_id()
* get_total_length()
* send_tracker_request()
* get_peer_list()
* get_num_pieces()
* get_num_blocks() 
* get_last_num_blocks()
* get_last_block_length()
* get_total_num_blocks()
* write_single_file()
* write_multiple_files()
* write_to_file()
* get_statistics() 
          
#### Description:
Configure a Torrent by reading in the important information of a .torrent file;    
Helper functions to get the file basic information and downloading status;
Send a the tracker a request for a peer list;    
Write out the corresponding files after download finishes;

	        
## 2. ConnectPeer:

#### Class:
	    PeerConnection(object):
	    	pstrlen 		   
	    	pstr      		   
	    	reserved           "\x00\x00\x00\x00\x00\x00\x00\x00"
	    	info_hash 		   torrent.info_hash
	    	peer_id            torrent.peer_id

	    PeerProtocol(Protocol):
			factory    		   Factory
			message_buffer     bytearray()
			message_timeout    time()

			#### Functions:
	        * connectionMade()
            * dataReceived(data)
            * handle_received_data(data)
            * connectionLost(reason)
            * get_response_msg(message_buffer)
            * get_next_send_msg(msg_type, msg_list, message_buffer, index, block_index)
            * get_next_request()

		Factory(ClientFactory):
			protocols 	       PeerProtocol[]
			torrent 		   Torrent
			download_finished  [bool]

			#### Functions:
	        * startedConnecting(connector)
            * buildProtocol(addr)
            * clientConnectionLost(connector,reason)
            * clientConnectionFailed(connector,reason)
            
#### Description:
Configure a peer connection with the torrent information, peer id and info hash;    
Build a protocol, start the TCP connection with the client;    
Handle the incoming TCP data properly based on the message type;


## 3. Message:

#### Functions:
* create_message(msg_type, index, begin, length, port)
* number_to_bytes(number)
* bytes_to_number(bytestring) 
          
#### Description:
Prepare a message to send based on the to-send message's type;  


================================================================================================================
                                            USAGE
================================================================================================================
#### Turn on:
* python driver.py TORRENT_FILE_NAME; 
* for example: python driver.py bub_ht_011203476_archive.torrent;
#### Valid Command:
* info: get the basic information about the torrent file;
* peers: get the peers that's currently connecting to;
* status: get the downloading status, including how many bytes that have been downloaded, and how many percentage that's completed;
* quit: quit the entire program


================================================================================================================
                                            DOWNLOADING ALGORITHM
================================================================================================================
#### Algorithm:
* First, loop through all peers to make TCP connection;
* Send the peers a Handshake message and wait for it's "Bitfield"/"Unchoke" messages;
* Once received the peer's "Unchoke" message, send 10 block requests to the peer;
* Every time when receving a "Piece" message, send the next block request where block is empty;


================================================================================================================
                                            PROBLEMS & BUGS
================================================================================================================
* Performance is very slow due to the piece requesting algorithm;
* It doesn't support seeding to other peers; only downloading from peers;

