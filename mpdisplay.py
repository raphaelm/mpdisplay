#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       hangman.py
#       
#       Copyright 2011 Raphael Michel <webmaster@raphaelmichel.de>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
import BaseHTTPServer
import json
import webbrowser
import thread
import time
import os
import random
import urllib
import mpd
import magic

typecache = {}
mime = magic.open(magic.MAGIC_MIME)
mime.load()

client = mpd.MPDClient(use_unicode=True)
client.connect("localhost", 6600, timeout=0.5)

class MpdisplayHTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def log_request(self, code=False, size=False):
		pass
		
	def do_GET(self):
		global typecache, client
		if self.path == "/status":
			retobj = {
				'status' : client.status(),
				'cs' : client.currentsong()
			}
			try:
				u = urllib.urlopen("http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key=b8258575158335e66482df0777e5b331&artist=%s&album=%s&format=json" % (urllib.quote(retobj['cs']['artist']), urllib.quote(retobj['cs']['album'])))
				lastfm = json.load(u)
				sizes = ('small', 'medium', 'large', 'extralarge', 'mega')
				last = -1
				if lastfm['album']['image']:
					for im in lastfm['album']['image']:
						if sizes.index(im['size']) > last:
							last = sizes.index(im['size'])
							retobj['cover'] = im['#text']
			except:
				pass
			self.wfile.write(json.dumps(retobj, indent=True))
			return
		if self.path == "/":
			self.path = "/index.html"
			
		filename = self.path[1:]
		if os.path.exists(filename):  
			if filename not in typecache:
				if filename[-4:] == ".css":
					t = 'text/css; charset=utf-8'
				elif filename[-3:] == ".js":
					t = 'text/javascript; charset=utf-8'
				elif filename[-5:] == ".html":
					t = 'text/html; charset=utf-8'
				elif filename[-4:] == ".png":
					t = 'image/png'
				else:
					t = mime.file(filename)
				typecache[filename] = t
			self.send_response(200)
			self.send_header("Content-type", typecache[filename])
			self.end_headers()
			f = open(filename)
			self.wfile.write(f.read())
			f.close()
		else:
			 self.send_error(404)
			
def openpage(stuff):
	time.sleep(0.5)
	webbrowser.open('http://localhost:54735/')
			
def main():	
	server_address = ('', 54735)
	httpd = BaseHTTPServer.HTTPServer(server_address, MpdisplayHTTPHandler)
	thread.start_new_thread(openpage, (None,))
	httpd.serve_forever()
	return 0

if __name__ == '__main__':
	main()

