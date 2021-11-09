import socketserver

class TCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
