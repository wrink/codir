import sublime, sublime_plugin
import time, difflib
from .codir_utils import history
from . import util_commands
class EditListener(sublime_plugin.EventListener):
	def on_new(self, view):
		print ('new view')
		history.push_history(view)

	def on_clone(self, view):
		print ('cloned view')
		history.push_history(view)

	def on_load(self, view):
		print ('loaded view')
		history.push_history(view)

	def on_modified(self, view):
		if history.is_insert(view):
			return
		else:
			history.push_history(view)

	def on_text_command(self, view, command_name, args):
		print (command_name)

		if command_name == 'codir_insert': history.insert[view.id()] = True
		elif command_name == 'undo':
			view.run_command('codir_undo')
			return 'CodirUndo'
		elif command_name == 'redo':
			print ('test')
			view.run_command('codir_redo')
			return 'CodirRedo'