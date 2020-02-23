from struct import Struct
from binascii import crc32

BODY_LEN = 32
PROTOCOL_ID = b'MHP'

START_MESSAGE_PACKET = 0
MESSAGE_PACKET = 1

# Define the pack format
protocol_format = '>'
protocol_format += '3s'           # 3 char protocol identifier ('MHP')
protocol_format += 'h'            # Frame counter (0-65535)
protocol_format += 'B'            # Packet type 
protocol_format += 'B'            # Message part counter (0-255)
protocol_format += 'B'            # Body length (0-32)
protocol_format += f'{BODY_LEN}s' # 32 byte frame body
# CRC32 checksum of everything is appended
protocol_struct = Struct(protocol_format)

class MessageError(Exception):
  pass

class Frame:
  def __init__(self, protocol_id, frame_count, packet_type, part_count, length, body):
    self.protocol_id = protocol_id
    self.frame_count = frame_count
    self.packet_type = packet_type
    self.part_count = part_count
    self.length = length
    self.body = body
  
  def pack(self):
    padded_body = self.body + b'\x00'*(BODY_LEN-self.length)
    packed = protocol_struct.pack(self.protocol_id, self.frame_count, self.packet_type, self.part_count, self.length, padded_body)
    checksum = crc32(packed)
    packed += checksum.to_bytes(4, 'big')
    return packed
  
  @staticmethod
  def unpack(packed):
    # Remove checksum from main payload
    checksum = packed[-4:]
    checksum = int.from_bytes(checksum, byteorder='big', signed=False)
    packed = packed[:-4]

    if crc32(packed) != checksum:
      raise MessageError('Invalid checksum')
    
    (protocol_id, frame_count, packet_type, part_count, length, body) = protocol_struct.unpack(packed)
    if protocol_id != PROTOCOL_ID:
      raise MessageError('Invalid protocol identifier')
    if length > BODY_LEN:
      raise MessageError('Invalid length')
    frame = Frame(protocol_id, frame_count, packet_type, part_count, length, body[:length])
    return frame

class TXProtocol:
  def __init__(self):
    self.frame_count = 0
    self.part_count = 0

  def pack(self, content):
    self.part_count = 0


  def pack_frame(self, body):
    length = len(body)
    frame = Frame(PROTOCOL_ID, self.frame_count, MESSAGE_PACKET, self.part_count, len(body))

    self.frame_count = (self.frame_count + 1) % 65536
    self.part_count = (self.part_count + 1) % 256
