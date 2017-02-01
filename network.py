import socket

class PeerNetwork:
    self.peers = []

    def make_socket():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SQL_SOCKET, socket. SOREUSEADDRk, 1)
        s.bind(('', port))
        s.listen(backlog=5)
        return s
