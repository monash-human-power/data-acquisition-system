from struct import Struct
from binascii import crc32

BODY_LEN = 32
PROTOCOL_ID = b'MHP'

MESSAGE_PACKET = 0
START_MESSAGE_PACKET = 1

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

start_message_format = '>h'       # Total message body size
start_message_struct = Struct(start_message_format)

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
    checksum = int.from_bytes(checksum, 'big')
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
  
  def _create_start_packet(self, message_length):
    body = start_message_struct.pack(message_length)
    frame = Frame(PROTOCOL_ID, self.frame_count, START_MESSAGE_PACKET, 0, 2, body)
    self.frame_count = (self.frame_count + 1) % 65536
    self.part_count = 1
    return frame.pack()

  def _create_message_packet(self, body):
    frame = Frame(PROTOCOL_ID, self.frame_count, MESSAGE_PACKET, self.part_count, len(body), body)
    self.frame_count = (self.frame_count + 1) % 65536
    self.part_count = (self.part_count + 1) % 256
    return frame.pack()

  def pack(self, content):
    content_bytes = content.encode('utf-8')
    length = len(content_bytes)
    chunks = []
    for i in range(0, length, BODY_LEN):
      chunks.append(content_bytes[i:i+BODY_LEN])
    
    frames = []
    frames.append(self._create_start_packet(length))
    for chunk in chunks:
      frames.append(self._create_message_packet(chunk))
    return frames

class RXProtocol:
  def __init__(self):
    self.frame_count = 0
    self.part_count = 0
    self.message = ''
    self.message_length = 0
    self.started_message = False
  
  def receive_packet(self, packet):
    try:
      frame = Frame.unpack(packet)
    except:
      # Malformed frame, discard the message
      self.started_message = False

    if frame.packet_type == START_MESSAGE_PACKET:
      (total_length,) = start_message_struct.unpack(frame.body)

      self.part_count = 0
      self.message = ''
      self.message_length = total_length
      self.started_message = True
    elif frame.packet_type == MESSAGE_PACKET:
      if self.started_message and frame.part_count == (self.part_count + 1) % 256:
        self.message += frame.body.decode('utf-8')
        self.message_length -= frame.length

        if self.message_length <= 0:
          # Message is done
          print(self.message)
          self.started_message = False

        self.part_count = frame.part_count
      else:
        # Stop processing this message and discard it
        self.started_message = False

    self.frame_count = frame.frame_count

if __name__ == "__main__":
  content = 'helloworldloremipsum1234567890_'*5

  tx = TXProtocol()
  rx = RXProtocol()
  packets = tx.pack(content)
  for packet in packets:
    rx.receive_packet(packet)
