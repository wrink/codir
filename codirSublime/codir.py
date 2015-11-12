import sublime, sublime_plugin
import socket, json, sys, threading, os, zipfile

class CodirServerCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.window().show_input_panel('Project name: ', 'New_project', self.initProj, None, None)

	def initProj(self, path):
		t = CodirServerThread('', 3000, sublime.active_window().folders(), path)
		t.start()

class CodirServerThread(threading.Thread):
	def __init__(self, host, port, project, path):
		self.host = host
		self.port = port
		self.project = 'projects/' + path + '.zip'
		self.path = path
		self.clients = []
		self.clientThreads = []
		self.isRecieving = False
		threading.Thread.__init__(self)

	def run(self):
		serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			serversocket.bind((self.host, self.port))
		except socket.error, e:
			sublime.error_message('Socket Bind Failed. Error Code: ' + str(e[0]) + ', Message: ' + e[1])
			print('Error: socket bind failed')
		print 'Bind succeeded'
		
		print 'Archiving project'
		if os.path.exists(self.project) == False:
			zipf = open(self.project, 'w')
			zipf.close()
		else:
			sublime.error_message('Error: project could not be created. Path: ' + self.project)
			return
		zipf = zipfile.ZipFile(self.project, 'w')
		for folder in self.project:
			zip(folder, self.project)

		serversocket.listen(10)
		print 'Listening on ' + str(self.host) + ':' + str(self.port)

		while True:
			(conn, addr) = serversocket.accept()
			print 'User Connected: ' + addr[0] + ':' + str(addr[1])

			t = CodirServerClientThread(conn, self)
			self.clients.append(conn)
			self.clientThreads.append(t)
			t.start()
		

	def zip(path, zipf):
		for root, dirs, files in os.walk(path):
			for file in files:
				zipf.write(os.path.join(root, file))


class CodirServerClientThread(threading.Thread):
	def __init__(self, conn, server):
		self.conn = conn
		self.server = server
		threading.Thread.__init__(self)

	def run(self):
		self.sendZip()

	def sendZip(self):
		zipf = open(self.server.project, 'rb')
		buffer =  zipf.read(1024)
		header = buffer
		while buffer:
			buffer = zipf.read(1024)
			header += buffer
		self.conn.sendall(header)
