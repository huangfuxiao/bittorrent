from message import bytes_to_number
from bitmap import BitMap
import os

BLOCK_SIZE = 2**14
PIECE_SIZE = 2**19

class Block(object):
    def __init__(self, index, block_length, block_content=''):
        self.index = index
        self.block_length = block_length
        self.block_content = block_content
        self.full = False

    def is_block_full(self):
        return self.full

    # def get_info(self):
    #     print 'length of block_content: ' + str(len(self.block_content))
    #     print 'block_length:            ' + str(self.block_length)
    #     print 'equal?                   ' + str(len(self.block_content) == self.block_length)

    def write(self, block_content):
        self.block_content = block_content 
        self.full = True

    def __repr__(self):
        return repr(self.block_content)

class Piece(object):
    def __init__(self, index, piece_length, file_to_write, piece_hash):
        self.index = index
        self.piece_length = piece_length
        self.num_blocks = piece_length/BLOCK_SIZE
        self.file_to_write = file_to_write
        self.piece_hash = piece_hash
        self.block_list = []
        for block in range(self.num_blocks):
            self.block_list.append(Block(block, BLOCK_SIZE))
        if piece_length % BLOCK_SIZE != 0:
            last_block_length = piece_length % BLOCK_SIZE
            self.block_list.append(Block(self.num_blocks, last_block_length))
            self.num_blocks = self.num_blocks + 1
        self.bitmap = BitMap(self.num_blocks)
        # if self.index == 16:
        #     print "init bm: ", self.bitmap 

    def is_piece_full(self):
        for block in range(len(self.block_list)):
            if not self.block_list[block].is_block_full():
                return False
        return True

    def fill_the_block(self, block_index, block_content):
        if self.block_list[block_index].is_block_full():
            return
        self.block_list[block_index].write(block_content)
        self.bitmap.set(block_index)


    def write(self):
        if self.bitmap.all():
            bytes_to_write = bytearray('')
            for block in self.block_list:
                bytes_to_write = bytes_to_write + block.block_content
            self.file_to_write.seek(self.index * self.piece_length)
            self.file_to_write.write(bytes_to_write)
            print self.index, self.piece_length
            print self.bitmap
            # print self.index


class FileWriter(object):
    def __init__(self, total_length, file_to_write, piece_hash_array):
        self.num_pieces = total_length / PIECE_SIZE
        self.piece_list = []
        for piece in range(self.num_pieces):
            self.piece_list.append(Piece(piece, PIECE_SIZE, file_to_write, piece_hash_array[piece]))
        if total_length % PIECE_SIZE != 0:
            last_piece_length = total_length % PIECE_SIZE
            self.piece_list.append(Piece(self.num_pieces, last_piece_length, file_to_write, piece_hash_array[self.num_pieces]))
            self.num_pieces = self.num_pieces + 1
        self.bitmap = BitMap(self.num_pieces)
        # print "self.num_pieces, init bm: ", self.num_pieces, self.bitmap

    def is_file_full(self):
        for piece in range(len(self.piece_list)):
            # print piece, self.piece_list[piece].bitmap.size()
            if not self.piece_list[piece].is_piece_full():
                return False
        return True

    def update_file_bitmap(self, piece_index):
        if self.piece_list[piece_index].bitmap.all():
            self.bitmap.set(piece_index)



