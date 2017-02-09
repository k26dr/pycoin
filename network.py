import argparse
import socket   
from socketserver import TCPServer, ThreadingMixIn, BaseRequestHandler
import threading
import signal
import sys
import struct
import pdb

class MessageHandler(BaseRequestHandler):
    def handle(self):
        header = PeerMessageHeader.unpack(self.request.recv(PeerMessageHeader.HEADER_LENGTH))
        payload = self.request.recv(header.payload_length)
        message = PeerMessage.from_header_payload(header, payload)
        response = getattr(self, message.header.command)(message)
        self.request.sendall(response.pack())

    def version(self, message):
        print("Incoming peer connection: {0}:{1}".format(message.header.ip, message.header.port))
        return PeerMessage('verack', '127.0.0.1', 8834)
        
    
class PycoinTCPServer(ThreadingMixIn, TCPServer):
    def __init__(self, *args):
        self.allow_reuse_addr = True
        super(PycoinTCPServer, self).__init__(*args)

class PeerMessage:
    def __init__(self, command, ip, port, payload=b''):
        self.header = PeerMessageHeader(command, ip, port, len(payload))
        self.payload = payload
        
    def pack(self):
        payload = self.payload
        return self.header.pack() + payload

    def send(self, peer):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(peer)
        sock.send(self.pack())
        header = PeerMessageHeader.unpack(sock.recv(PeerMessageHeader.HEADER_LENGTH))
        payload = sock.recv(header.payload_length)
        sock.close()
        message = PeerMessage.from_header_payload(header, payload)
        return message
        
        
    @classmethod
    def from_header_payload(cls, header, payload):
        return PeerMessage(header.command, header.ip, header.port, payload)


class PeerMessageHeader:
    HEADER_LENGTH=22

    def __init__(self, command, ip, port, payload_length):
        self.command = command
        self.ip = ip
        self.port = port
        self.payload_length = payload_length
    
    def pack(self):
        command = self.command.encode('ascii') + b'\x00' * (12 - len(self.command))
        ip_parts = [int(i) for i in self.ip.split('.')]
        return struct.pack('=12sBBBBHI', command, *ip_parts, self.port, self.payload_length)

    @classmethod
    def unpack(self, header_struct):
        command, ip, port, payload_length = struct.unpack('=12s4sHI', header_struct)
        command = command.replace(b'\x00', b'').decode('ascii')
        ip = '.'.join([str(b) for b in ip])
        return PeerMessageHeader(command, ip, port, payload_length)

class PeerNetwork:
    TRACKER_NODE = ('127.0.0.1', 8834)

    def __init__(self, host='127.0.0.1', port=8834):
        self.host = host
        self.port = port
        self.peers = set()
        self.server = PycoinTCPServer((host, port), MessageHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()
        self.connect_to_peer(*self.TRACKER_NODE)

    def connect_to_peer(self, peerhost, peerport):
        message = PeerMessage('version', self.host, self.port)
        response = message.send((peerhost, peerport))
        if response.header.command == 'verack':
            self.peers.add((peerhost, peerport))

    def close(self):
        self.server.shutdown()
        self.server.server_close()

def cleanup(signal, frame):
    network.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=8834, type=int)
    args = parser.parse_args()
    network = PeerNetwork(port=args.port)
    signal.signal(signal.SIGINT, cleanup)
