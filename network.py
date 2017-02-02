from socketserver import ThreadingTCPServer, BaseRequestHandler
import threading

class MessagHandler(BaseRequestHandler):
    def handle(self):
        self.request.sendall(b'hello\n')
    

class PeerNetwork:
    PEER_TRACKER = ('localhost', 8834)

    def __init__(self, host='localhost', port=8834):
        self.peers = []
        self.server = ThreadingTCPServer((host, port), MessageHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()

    def find_peers(self):
        pass

if __name__ == '__main__':
    network = PeerNetwork()
