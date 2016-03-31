#!/usr/bin/env python3

from server.server import Server

if __name__ == "__main__":
    server = Server(host='', port=8080)
    server.run()