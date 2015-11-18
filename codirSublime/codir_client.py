#!/usr/bin/env python2.7
import sublime, sublime_plugin
import threading, re, zipfile
import sys, os
path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, path + '/socketIO')
from socketIO_client import SocketIO, BaseNamespace, LoggingNamespace

global sockets

sockets = {}

class CodirClientCommand(sublime_plugin.WindowCommand):
	def run(self):		
		self.window.show_input_panel('ShareID', '', self.verify_shareid, None, None)

	def verify_shareid(self, shareid):
		if re.match(r'((^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|(localhost)):\d{1,4}$', shareid):
			t = ClientThread(shareid)
			t.start()
		else:
	 		sublime.error_message('ERROR: ' + shareid + 'is not a valid ShareID')

class ClientThread(threading.Thread):
	def __init__(self, shareid):
		self.shareid = shareid
		threading.Thread.__init__(self)
		
	def run(self):
		sublime.run_command('new_window')
		self.window = sublime.active_window()

		host, port = self.shareid.split(':')
		self.socket = SocketIO(host, int(port), LoggingNamespace)

		sockets[self.window.id()] = {'socket': self.socket, 'window': self.window, 'shareid': shareid}
		
		self.socket.on('live-file-connection', self.download)

		#self.socket

		self.socket.emit('live-file-connection', '')
		while True:
			self.socket.wait(seconds=1)

	def download(self, *file):
		print ('start')

		if not os.path.exists(path + '/projects'):
			os.makedirs(path + '/projects')

		fp = os.path.relpath(path + '/projects')
		print (fp)

		f = open(fp + '/' + self.shareid + '.zip', 'wb+')
		f.write(bytes.fromhex(file[0]))
		f.close()

		if not os.path.exists(path + '/projects'):
			os.makedirs(path + '/projects/' + self.shareid)

		z = zipfile.ZipFile(path + '/projects/' + self.shareid + '.zip', 'r')
		z.extractall(path + '/projects/' + self.shareid + '/')
		
		self.set_project_data({'folders': [ {'path': path + '/projects/' + self.shareid + '/'} ] })
		print ('done')