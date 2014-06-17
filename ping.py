import socket
import struct
import json


def unpack_varint(s):
    d = 0
    for i in range(5):
        b = ord(s.recv(1))
        d |= (b & 0x7F) << 7 * i
        if not b & 0x80:
            break
    return d


def pack_varint(d):
    o = ""
    while True:
        b = d & 0x7F
        d >>= 7
        o += struct.pack("B", b | (0x80 if d > 0 else 0))
        if d == 0:
            break
    return o


def pack_data(d):
    return pack_varint(len(d)) + d


def pack_port(i):
    return struct.pack('>H', i)


# stolen from https://gist.github.com/barneygale/1209061

def get_info(host='localhost', port=25565):
    # Connect
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)

    try:
        s.connect((host, port))
    except:
        return False

    # Send handshake + status request
    s.send(pack_data("\x00\x00" + pack_data(host.encode('utf8'))
                     + pack_port(port) + "\x01"))
    s.send(pack_data("\x00"))

    # Read response
    unpack_varint(s)   # Packet length
    unpack_varint(s)   # Packet ID
    l = unpack_varint(s)  # String length

    d = ""
    while len(d) < l:
        d += s.recv(1024)

    # Close our socket
    s.close()

    # Load json and return
    return json.loads(d.decode('utf8'))


# stolen from http://pastebin.com/ZavsWG60

def get_info_old(host='localhost', port=25565):
    # Set up our socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # Send 0xFE: Server list ping
    s.send('\xfe\x01')

    # Read some data
    d = s.recv(1024)
    s.close()

    # Check we've got a 0xFF Disconnect
    assert d[0] == '\xff'

    # Remove the packet ident (0xFF) and the short containing the length of the string
    # Decode UCS-2 string
    d = d[3:].decode('utf-16be')

    # Check the first 3 characters of the string are what we expect
    assert d[:3] == u'\xa7\x31\x00'

    # Split
    d = d[3:].split('\x00')

    # Return a dict of values
    return {'protocol_version': int(d[0]),
            'server_version':       d[1],
            'motd':                 d[2],
            'players':          int(d[3]),
            'max_players':      int(d[4])}
