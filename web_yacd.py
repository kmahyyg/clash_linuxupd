#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import http.server
import socketserver
import os

PORT = 62038

os.chdir(os.path.expanduser("~/.local/clash_linuxupd/yacd"))

Handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("127.0.0.1", PORT), Handler)
print("Serving at port", PORT)
httpd.serve_forever()
