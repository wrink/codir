from socketIO_client import SocketIO, LoggingNamespace
import sublime, sublime_plugin, threading

isRemoteEdit = threading.Lock()

class CodirClientCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		print 'test'
		self.view.window().show_input_panel('Project id: ', 'localhost:3000', self.connect, None, None)

	def connect(self, shareid):
		t = SocketThread(shareid)
		t.start()


class SocketThread(threading.Thread):
	def __init__(self, shareid):
		self.HOST, self.PORT = shareid.split(':')
		threading.Thread.__init__(self)
	def run(self):
		a = 1
#		socket = SocketIO(self.HOST, int(self.PORT), LoggingNamespace)
#
#		socket.on('new connection update', self.newConnection)
#	def newConnection(file):
#		pass



class SocketEventListener(sublime_plugin.EventListener):
	def __init__(self):
		self.buffers = {}
#	def on_modified(self, view):
#		print self.buffers[view.id()]

	def on_load(self, view):
		self.buffers[view.id()] = view.substr(sublime.Region(0, view.size()))

class TestCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.insert(edit, 0, '#test\n')

# import sublime, sublime_plugin
# import socket, json, sys, threading, os, zipfile

# class CodirClientCommand(sublime_plugin.TextCommand):
# 	def run(self, edit):
# 		self.view.window().show_input_panel('Project id: ', 'localhost:3000', self.connect, None, None)

# 	def connect(self, e):
# 		portAndHost = str(e)

# 		if portAndHost.find(':') == -1 :
# 			sublime.error_message('Error: that is not a valid socket')
# 			return

# 		HOST = portAndHost[0 : -5]
# 		PORT = int(portAndHost[-4:])

# 		print HOST + ':' + str(PORT)

# 		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 		try:
# 			s.connect((HOST, PORT))
# 		except socket.error, e:
# 			sublime.error_message('Socket Connect Failed. Error Code: ' + str(e[0]) + ', Message: ' + e[1])
# 			return

# 		panel = self.view.window().show_input_panel('Save to: ', '~/', self.save, None, None)

# 	def save(self, root):
# 		path = os.path.join(root, 'project.zip')

# 		if os.path.exists(path):
# 			sublime.error_message('Error: project already exists at target location')
# 			return
# 		elif os.access(os.path.dirname(path), os.W_OK) == False:
# 			sublime.error_message('Error: location either does not exist or cannot be written to')
# 			return

# 		proj = open(path, wb)
# 		buffer = recv(4096)
# 		while buffer:
# 			proj.write(buffer)
# 			buffer = recv(4096)

# 		proj.close()
# 		proj.open(path, rb)
# 		z = zipfile.ZipFile(proj)
# 		for name in z.namelist():
# 			z.extract(name, root)