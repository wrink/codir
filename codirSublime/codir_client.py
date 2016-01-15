import sublime, sublime_plugin
import threading, re, zipfile
import sys, os, time, json
import binascii
from . import history
path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, path + '/socketIO')
from socketIO_client import SocketIO, BaseNamespace, LoggingNamespace

global sockets
global windows

windows = {}
sockets = {}

class CodirClientCommand(sublime_plugin.WindowCommand):
	def run(self):		
		self.window.show_input_panel('ShareID', 'localhost:8000', self.verify_shareid, None, None)

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
		print ('test0')
		self.socket = SocketIO(host, int(port), LoggingNamespace)
		print ('test1')
		
		self.socket.on('live-file-connection', self.download)

		self.socket.on('workspace-file-edit-update', self.apply)

		self.socket.on('workspace-open-file-update', self.apply_all)
		print ('test2')
		self.socket.emit('live-file-connection', '')
		while True:
			self.socket.wait(seconds=1)

	def download(self, file):
		print ('start')
		self.shareid = file['shareid']
		sockets[self.window.id()] = {'socket': self.socket, 'window': self.window, 'shareid': self.shareid}

		if not os.path.exists(path + '/projects'):
			os.makedirs(path + '/projects')

		fp = os.path.relpath(path + '/projects')
		print (fp)

		f = open(fp + '/' + self.shareid + '.zip', 'wb+')
		f.write(bytes.fromhex(file['zip']))
		f.close()

		if not os.path.exists(path + '/projects'):
			os.makedirs(path + '/projects/' + self.shareid)

		z = zipfile.ZipFile(path + '/projects/' + self.shareid + '.zip', 'r')
		z.extractall(path + '/projects/' + self.shareid + '/')
		z.close()

		folders = []
		folders += [{'path': path + '/projects/' + self.shareid + '/' + f} for f in os.listdir(path + '/projects/' + self.shareid + '/') if '.DS_Store' not in f]
		
		#self.window.set_project_data({'folders': [ {'path': path + '/projects/' + self.shareid + '/'} ] })
		self.window.set_project_data({'folders': folders })
		windows[self.window.id()] = ProjectWatcher(self.window, self.shareid)
		windows[self.window.id()].start()
		print ('done')

	def apply(self, delta):
		path = os.path.dirname(os.path.realpath(__file__)) + '/projects/' + self.shareid + '/' + delta['path']

		views = self.window.views()
		for view in views:
			filename = view.file_name()
			if path in filename and filename.index(path) + len(path) == len(filename):
				view.run_command('apply_deltas', {'deltas': delta['deltas']})
				#history.delta_queue[view.id()].append(delta['deltas'])

	def apply_all(self, deltas):
		for delta in deltas['deltas']:
			path = os.path.dirname(os.path.realpath(__file__)) + '/projects/' + self.shareid + '/' + deltas['path']

			views = self.window.views()
			for view in views:
				filename = view.file_name()
				if path in filename and filename.index(path) + len(path) == len(filename):
					view.run_command('apply_deltas', {'deltas': delta})

class ProjectWatcher(threading.Thread):
	def __init__(self, window, shareid):
		self.shareid = shareid
		self.window = window
		self.socket = sockets[self.window.id()]['socket']
		self.project_data = window.project_data()['folders']
		self.contents = self.get_contents(self.project_data)
		self.incoming = False
		threading.Thread.__init__(self)
	
	def run(self):
		while 1:
			if not self.window.id() in windows: return
			before = self.contents
			self.project_data = self.window.project_data()['folders']
			after = self.get_contents(self.project_data)
			self.contents = after

			if before == after:
				time.sleep(1)
				continue
			print('test')
			#added = [f for f in after if not f in before]
			#removed = [f for f in before if not f in after]
			added, removed = [], []
			for f in after:
				if not f in before:
					added += [f]
			for f in before:
				if not f in after:
					removed += [f]
			
			if not self.check_incoming():

				add, rem = [], []
				for f in added:
					is_root = True
					for r in add:
						if r in f and f.index(r) == 0:
							is_root = False
							break
					if is_root:
						add.append(f)
				for f in removed:
					is_root = True
					for r in rem:
						if r in f and f.index(r) == 0:
							is_root = False
							break
					if is_root:
						rem.append(f)

				fp = os.path.relpath(path + '/projects/' + self.shareid) + '/';

				z = zipfile.ZipFile(fp + '.fdeltas.zip', 'w')
				prefix = ''
				for f in added:
					if prefix in f and prefix != '':
						start = f.index(prefix) + len(prefix)
						z.write(f, arcname=f[start:])
						print(f[start+1:])
					else:
						prefix = os.path.dirname(f)
						z.write(f, arcname=os.path.basename(f))
						print(os.path.basename(f))

				fdeltas = {'added': {}, 'removed': {}}

				for f in add:
					if path in f:
						prefix = os.path.join(path, 'projects', self.shareid)
						index = f.index(prefix)
						print(os.path.dirname(f)[index+len(prefix):])
						fdeltas['added'][f[index+len(prefix):]] = os.path.dirname(f)[index+len(prefix):]
					# else:
					# 	fdeltas['added'][os.path.basename(f)] = None
				for f in rem:
					prefix = os.path.join(path, 'projects', self.shareid)
					index = f.index(prefix)
					fdeltas['removed'][f[index+len(prefix):]] = None
				
				f = open(fp + '.fdeltas.json', 'w')
				json.dump(fdeltas, f)
				f.close()
				z.write(os.path.relpath(fp + '.fdeltas.json'), arcname='.fdeltas.json')
				z.close()

				z = open(fp + '.fdeltas.zip', 'rb')
				emit = str(binascii.hexlify(z.read()))
				print(emit)
				self.socket.emit('workspace-project-edit-update', emit)

				z.close()

				os.remove(fp + '.fdeltas.json')
				os.remove(fp + '.fdeltas.zip')
				# self.incoming = True

	def get_contents(self, folders):
		ret = []
		for folder in self.project_data:
			#print('get_contents of '+ folder['path'])
			ret.append(folder)
			for root, dirs, files in os.walk(folder['path']):
				ret+=[os.path.join(root, directory) for directory in dirs]
				ret+=[os.path.join(root, f) for f in files]
		return ret

	def check_incoming(self):
		if self.incoming:
			self.incoming = False
			return True
		return False