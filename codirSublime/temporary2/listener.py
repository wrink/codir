import sublime, sublime_plugin
import time, threading, os
from .codir_utils import history, utils
from . import util_commands
from . import codir_client as CC

global lock
lock = False

class EditListener(sublime_plugin.EventListener):
	def __init__(self):
		self.lock = threading.RLock()
		self.emitlock = threading.RLock()
		self.deltalock = threading.RLock()
		sublime_plugin.EventListener.__init__(self)

	def on_activated(self, view):
		if view.id() not in history.buffer_history:
			history.init_view(view)

	def on_new(self, view):
		print ('new view')
		history.init_view(view)

	def on_clone(self, view):
		print ('cloned view')
		history.init_view(view)

	def on_load(self, view):
		print ('loaded view')
		history.init_view(view)
		if view.window().id() in CC.sockets:
			socket = CC.sockets[view.window().id()]
			dir = os.path.dirname(os.path.abspath(__file__)) + '/' + socket['shareid'] + '/'
			filename = view.file_name()
			if dir in filename:
				sub_path = filename[filename.index(dir) + len(dir):]
				event = {'shareid': socket['shareid'], 'path': sub_path}
				socket['socket'].emit('workspace-open-file-update', event)
				print(event)

	# def on_modified(self, view):
	# 	if history.is_insert(view, external_bit=1):
	# 		return
	# 	else:
	# 		self.emitlock.acquire()
	# 		deltas = history.get_deltas(view)

	# 		id = view.id()

	# 		if id in history.delta_queue[id]:
	# 			for delta in history.delta_queue[id]:
	# 				utils.apply_deltas_to_deltas(deltas, delta)
	# 				view.run_command('apply_deltas', deltas, 1)
	# 				history.delta_queue[id] = history.delta_queue[id][1:]
	# 		self.emitlock.release()

	def on_modified_async(self, view):

		if history.is_insert(view):
			print('is_insert')
			return
		else:
			# path = 'codirSublime/projects/'
			# id = view.id()
			# file = view.file_name()

			# self.deltalock.acquire()
			# deltas = history.get_deltas(view)
			# print(deltas)
			# print(history.history_counter[id])
			# print(history.buffer_history[id])
			# if not id in history.buffer_history: history.buffer_history[id] = {}
			# history.buffer_history[id][history.millis()] = view.substr(sublime.Region(0, view.size()))
			# self.deltalock.release()
			
			# if id in CC.sockets and file.index(path) > 0:
			# 	path_start = file.index(path) + len(path + CC.sockets[id]['shareid'] + '/')
			# 	CC.sockets[id]['socket'].emit('workspace-file-edit-update', {'path': file[path_start:], 'deltas': deltas, 'shareid': CC.sockets[id]['shareid']})

			# if id in history.delta_queue:
			# 	for delta in history.delta_queue[id]:
			# 		utils.apply_deltas_to_deltas(deltas, delta)
			# 		view.run_command('apply_deltas', deltas, 1)
			# 		history.delta_queue[id] = history.delta_queue[id][1:]

			t = history.millis()
			self.lock.acquire()
			#global lock
			#while lock:
			#	time.sleep(0.01)
			#lock = True
			#print (t)
			print (history.millis() - t)
			# if history.millis()-t < 0.0085:
			# 	print ('same edit')
			# 	self.lock.release()
			# 	#lock = False
			# 	return
			
			time.sleep(0.2)

			# path = 'codirSublime/projects/'
			# id = view.id()
			# file = view.file_name()

			# self.deltalock.acquire()
			# deltas = history.get_deltas(view)
			# if not id in history.buffer_history: history.buffer_history[id] = {}
			# history.buffer_history[id][history.millis()] = view.substr(sublime.Region(0, view.size()))
			# self.deltalock.release()
			
			# if id in CC.sockets and file.index(path) > 0:
			# 	path_start = file.index(path) + len(path + CC.sockets[id]['shareid'] + '/')
			# 	CC.sockets[id]['socket'].emit('workspace-file-edit-update', {'path': file[path_start:], 'deltas': deltas, 'shareid': CC.sockets[id]['shareid']})

			# if id in history.delta_queue:
			# 	for delta in history.delta_queue[id]:
			# 		utils.apply_deltas_to_deltas(deltas, delta)
			# 		view.run_command('apply_deltas', deltas, 1)
			# 		history.delta_queue[id] = history.delta_queue[id][1:]

			history.push_history(view)

			lock = False
			self.lock.release()

	def on_text_command(self, view, command_name, args):
		print (command_name)

		# if command_name == 'undo':
		# 	view.run_command('codir_undo')
		# 	return 'CodirUndo'
		# elif command_name == 'redo':
		# 	view.run_command('codir_redo')
		# 	return 'CodirRedo'
		# elif command_name == 'commit_completion':
		# 	history.push_history(view)