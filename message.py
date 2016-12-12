TEST_HAVE_PIECE_INDEX = 99
TEST_REQ_PIECE_INDEX = 0
TEST_REQ_BLOCK_INDEX = 0
TEST_LISTEN_PORT = 8888
BLOCK_SIZE = 2**14

def number_to_bytes(number):  
    '''returns a number 4 bytes long'''
    if number < 255:
        length = '\x00\x00\x00' + chr(number)
    elif number < 256**2:
        length = '\x00\x00' + chr((number)/256) + chr((number) % 256)
    elif number < 256**3:
        length = ('\x00'+ chr((number)/256**2) + chr(((number) % 256**2) / 256) +
            chr(((number) % 256**2) % 256))
    else:
        length = (chr((number)/256**3) + chr(((number)%256**3)/256**2) + chr((((number)%256**3)%256**2)/256) + chr((((number)%256**3)%256**2)%256))
    return length

def bytes_to_number(bytestring):  
    '''bytestring assumed to be 4 bytes long and represents 1 number'''
    number = 0
    i = 3
    for byte in bytestring:
        try:
            number += ord(byte) * 256**i
        except(TypeError):
            number += byte * 256**i
        i -= 1
    return number

def create_message(msg_type, index, begin, length, port):
    if(msg_type == 'KEEPALIVE'):
        return_msg = number_to_bytes(0)
    elif(msg_type == 'CHOKE'):
        return_msg = number_to_bytes(1) + chr(0)
    elif(msg_type == 'UNCHOKE'):
        return_msg = number_to_bytes(1) + chr(1)
    elif(msg_type == 'INTERESTED'):
        return_msg = number_to_bytes(1) + chr(2)
    elif(msg_type == 'NOTINTERESTED'):
        return_msg = number_to_bytes(1) + chr(3)
    elif(msg_type == 'HAVE'):
        return_msg = number_to_bytes(5) + chr(4) + chr(index)
    elif(msg_type == 'BITFIELD'):
        return_msg = number_to_bytes(1) + chr(5)
    elif(msg_type == 'REQUEST'):
        return_msg = number_to_bytes(13)+ chr(6) + number_to_bytes(index) + number_to_bytes(begin) + number_to_bytes(length)
    elif(msg_type == 'PIECE'):
        return_msg = number_to_bytes(9) + chr(7) + number_to_bytes(index) + number_to_bytes(begin)
    elif(msg_type == 'CANCEL'):
        return_msg = number_to_bytes(13) + chr(8) + number_to_bytes(index) + number_to_bytes(begin)
    elif(msg_type == 'PORT'):
        return_msg = number_to_bytes(3) + chr(9) + number_to_bytes(port)
    return return_msg
    
