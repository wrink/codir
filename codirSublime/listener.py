import sublime, sublime_plugin
import time, threading, os
from .codir_utils import history
from . import util_commands
from . import codir_client as CC

class EditListener(sublime_plugin.EventListener):
	def __init__(self):
		self.lock = threading.RLock()
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

	def on_modified_async(self, view):
		if history.is_insert(view):
			return
		else:
			path = 'codirSublime/projects/'
			id = view.window().id()
			file = view.file_name()
			deltas = history.get_deltas(view)
			
			if id in CC.sockets and file.index(path) > 0:
				path_start = file.index(path) + len(path + CC.sockets[id]['shareid'] + '/')
				CC.sockets[id]['socket'].emit('buffer-modification-upate', {'file': file[path_start:], 'deltas': deltas})

			t = history.millis()
			self.lock.acquire()
			if t-history.millis() > 0.19:
				self.lock.release()
				return
			
			time.sleep(0.2)
			history.push_history(view)

			self.lock.release()

	def on_text_command(self, view, command_name, args):
		print (command_name)

		if command_name == 'undo':
			view.run_command('codir_undo')
			return 'CodirUndo'
		elif command_name == 'redo':
			view.run_command('codir_redo')
			return 'CodirRedo'