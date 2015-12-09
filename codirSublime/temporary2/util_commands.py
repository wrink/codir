import sublime, sublime_plugin
import difflib, threading
from .codir_utils import history, utils

class CodirUndoCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		curr = view.substr(sublime.Region(0, view.size()))
		buff, delta = history.get_undo(view)
		if delta == 0:
			print('delta = 0')
			return

		old_to_new = {'additions': {}, 'removals': {}}
		for i, s in enumerate(difflib.ndiff(buff, curr)):
			if s[0] == ' ': continue
			elif s[0] == '-':
				old_to_new['removals'][i] = s[-1]
			elif s[0] == '+':
				old_to_new['additions'][i] = s[-1]

		print(len(history.edit_history[view.id()]))
		delta = utils.remove_deltas_from_deltas(old_to_new, delta)
		print(delta)
		# NEW ONE
		# for i in sorted(old_to_new['additions'].keys()):
		# 	for j in reversed(sorted(delta['additions'].keys())):
		# 		if i <= j:
		# 			delta['additions'][j+1] = delta['additions'][j]
		# 			del delta['additions'][j]
		# 	for j in reversed(sorted(delta['removals'].keys())):
		# 		if i <= j:
		# 			delta['removals'][j+1] = delta['removals'][j]
		# 			del delta['removals'][j]
		# for i in reversed(sorted(old_to_new['removals'].keys())):
		# 	for j in sorted(delta['additions'].keys()):
		# 		if i < j:
		# 			delta['additions'][j-1] = delta['additions'][j]
		# 			del delta['additions'][j]
		# 		elif i == j and old_to_new['removals'][i] == delta['additions'][j]:
		# 			del delta['additions'][j]
		# 			for k in sorted(delta['additions'].keys()):
		# 				if j < k:
		# 					delta['additions'][k-1] = delta['additions'][k]
		# 					del delta['additions'][k]
		# 			for k in sorted(delta['removals'].keys()):
		# 				if j < k:
		# 					delta['removals'][k-1] = delta['removals'][k]
		# 					del delta['removals'][k]
		# 	for j in sorted(delta['removals'].keys()):
		# 		if i < j:
		# 			delta['removals'][j-1] = delta['removals'][j]
		# 			del delta['removals'][j]

		utils.remove_deltas(edit, view, delta)
		history.buffer_history[view.id()][history.millis()] = view.substr(sublime.Region(0, view.size()))

class CodirRedoCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		curr = view.substr(sublime.Region(0, view.size()))
		buff, delta = history.get_redo(view)

		if delta == 0:
			return

		old_to_new = {'additions': {}, 'removals': {}}
		for i, s in enumerate(difflib.ndiff(buff, curr)):
			if s[0] == ' ': continue
			elif s[0] == '-':
				old_to_new['removals'][i] = s[-1]
			elif s[0] == '+':
				old_to_new['additions'][i] = s[-1]

		delta = utils.apply_deltas_to_deltas(old_to_new, delta)
		print(delta)
		
		# NEW ONE
		# for i in sorted(old_to_new['additions'].keys()):
		# 	for j in reversed(sorted(delta['additions'].keys())):
		# 		if i <= j:
		# 			delta['additions'][j+1] = delta['additions'][j]
		# 			del delta['additions'][j]
		# 	for j in reversed(sorted(delta['removals'].keys())):
		# 		if i <= j:
		# 			delta['removals'][j+1] = delta['removals'][j]
		# 			del delta['removals'][j]
		# for i in reversed(sorted(old_to_new['removals'].keys())):
		# 	for j in sorted(delta['additions'].keys()):
		# 		if i < j:
		# 			delta['additions'][j-1] = delta['additions'][j]
		# 			del delta['additions'][j]
		# 	for j in sorted(delta['removals'].keys()):
		# 		if i < j:
		# 			delta['removals'][j-1] = delta['removals'][j]
		# 			del delta['removals'][j]
		# 		elif i == j and old_to_new['removals'][i] == delta['removals'][j]:
		# 			del delta['removals'][j]
		# 			for k in sorted(delta['additions'].keys()):
		# 				if j < k:
		# 					delta['additions'][k-1] = delta['additions'][k]
		# 					del delta['additions'][k]
		# 			for k in sorted(delta['removals'].keys()):
		# 				if j < k:
		# 					delta['removals'][k-1] = delta['removals'][k]
		# 					del delta['removals'][k]

		utils.apply_deltas(edit, view, delta)
		# NEW ONE
		# for i in sorted(delta['additions'].keys()):
		# #	history.insert[view.id()][0] = True
		# 	history.insert[view.id()][0] = True
		# 	view.insert(edit, i, delta['additions'][i])
		# for i in reversed(sorted(delta['removals'].keys())):
		# #	history.insert[view.id()][0] = True
		# 	history.insert[view.id()][0] = True
		# 	view.erase(edit, sublime.Region(i, i+1))

		history.buffer_history[view.id()][history.millis()] = view.substr(sublime.Region(0, view.size()))
		

class ApplyDeltasCommand(sublime_plugin.TextCommand):
	def run(self, edit, *args):
		utils.apply_deltas(edit, self.view, args[0], args[1])

class InsertCommand(sublime_plugin.TextCommand):
	def run(self, edit, *args):
		self.view.insert(edit, args[0], args[1])
		