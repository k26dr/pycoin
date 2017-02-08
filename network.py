import argparse
import socket   
from socketserver import TCPServer, ThreadingMixIn, BaseRequestHandler
import threading
import signal
import sys
import struct

class MessageHandler(BaseRequestHandler):
    def handle(self):
        header = self.request.recv(PeerMessage.HEADER_LENGTH)
        payload_length = int.from_bytes(header[12:PeerMessage.HEADER_LENGTH], 'little')
        payload = self.request.recv(payload_length)
        message = PeerMessage.unpack(header + payload)
        response = getattr(self, message.command)(message)
        self.request.sendall(response)

    def version(self, message):
        print("Incoming peer connection: {0}:{1}".format(message.ip, message.port))
        return b'verack'
        
    
class PycoinTCPServer(ThreadingMixIn, TCPServer):
    def __init__(self, *args):
        self.allow_reuse_addr = True
        super(PycoinTCPServer, self).__init__(*args)

class PeerMessage:
    HEADER_LENGTH=18

    def __init__(self, command, ip, port, payload=''):
        self.command = command
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.payload = payload
        
    def pack(self):
        command = self.command.encode('ascii') + b'\x00' * (8 - len(self.command))
        ip_parts = [int(i) for i in self.ip.split('.')]
        msg_length = len(self.payload)
        header = struct.pack('8sBBBBHL', command, *ip_parts, self.port, msg_length)
        print(header)
        payload = self.payload.encode('utf-8')
        return header + payload
    
    @classmethod
    def unpack(cls, msg):
        header = msg[0:cls.HEADER_LENGTH]
        payload = msg[cls.HEADER_LENGTH:].decode('utf-8')
        command, ip, port, msg_length = struct.unpack('8s4sHL', header)
        command = header[0:8].decode('ascii').replace('\x00','')
        ip = '.'.join([int.from_bytes(b, 'little') for b in msg[9:12]])
        port = int.from_bytes(msg[12:14], 'little')
        return PeerMessage(command, ip, port, payload)

class PeerNetwork:
    TRACKER_NODE = ('127.0.0.1', 8834)

    def __init__(self, host='127.0.0.1', port=8834):
        self.host = host
        self.port = port
        self.peers = set()
        self.sockets = []
        self.server = PycoinTCPServer((host, port), MessageHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()
        self.connect_to_peer(*self.TRACKER_NODE)

    def connect_to_peer(self, peerhost, peerport):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockets.append(sock)
        sock.connect((peerhost, peerport))
        message = PeerMessage('version', self.host, self.port)
        sock.send(message.pack())
        data = sock.recv(1024)
        if data == b'verack':
            self.peers.add((peerhost, peerport))
        sock.close()

    def find_peers(self):
        pass

    def close(self):
        for s in network.sockets:
            s.close()
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
