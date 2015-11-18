import sublime, sublime_plugin
import difflib, threading
from .codir_utils import history, utils

class CodirUndoCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		curr = view.substr(sublime.Region(0, view.size()))
		buff, delta = history.get_undo(view)
		if delta == 0: return

		old_to_new = {'additions': {}, 'removals': {}}
		for i, s in enumerate(difflib.ndiff(buff, curr)):
			if s[0] == ' ': continue
			elif s[0] == '-':
				old_to_new['removals'][i] = s[-1]
			elif s[0] == '+':
				old_to_new['additions'][i] = s[-1]

		delta = utils.remove_deltas_from_deltas(old_to_new, delta)

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

		print (delta)

		utils.remove_deltas(edit, view, delta)
		# for i in sorted(delta['removals'].keys()):
		# #	history.insert[view.id()][0] = True
		# 	history.insert[view.id()][0] = True
		# 	view.insert(edit, i, delta['removals'][i])
		# for i in reversed(sorted(delta['additions'].keys())):
		# # 	history.insert[view.id()][0] = True
		# 	history.insert[view.id()][0] = True
		# 	view.erase(edit, sublime.Region(i, i+1))

		history.buffer_history[view.id()][history.millis()] = view.substr(sublime.Region(0, view.size()))
		# print (history.edit_history[self.view.id()])
		
		# view = self.view
		# curr = self.view.substr(sublime.Region(0, self.view.size()))
		# buff, delta = history.get_undo(view)
		# if buff == 0 and delta == 0: return

		# old_to_new = {'additions': {}, 'removals': {}}
		# for i, s in enumerate(difflib.ndiff(buff, curr)):
		# 	if s[0] == ' ': continue
		# 	elif s[0] == '-':
		# 		old_to_new['removals'][i] = s[-1] 
		# 	elif s[0] == '+':
		# 		old_to_new['additions'][i] = s[-1]

		# for i in sorted(old_to_new['additions'].keys()):
		# 	for j in reversed(sorted(delta['additions'].keys())):
		# 		if i <= j:
		# 			delta['additions'][j+1] = delta['additions'][j]
		# 			del delta['additions'][j]
		# 	for j in reversed(sorted(delta['removals'].keys())):
		# 		if i <= j:
		# 			delta['removals'][j+1] = delta['removals'][j]
		# 			del delta['removals'][j]
		# for i in sorted(old_to_new['removals'].keys()):
		# 	for j in sorted(delta['additions'].keys()):
		# 		if i == j: del delta['additions'][j]
		# 		elif i < j:
		# 			delta['additions'][j-1] = delta['additions'][j]
		# 			del delta['additions'][j]
		# 	for j in sorted(delta['removals'].keys()):
		# 		if i < j:
		# 			delta['removals'][j-1] = delta['removals'][j]
		# 			del delta['removals'][j]

		# for i in sorted(delta['removals'].keys()):
		# 	history.insert[view.id()] = [True, True];
		# 	self.view.insert(edit, i, delta['removals'][i])
		# for i in reversed(sorted(delta['additions'].keys())):
		# 	history.insert[view.id()] = [True, True];
		# 	self.view.erase(edit, sublime.Region(i, i+1))

class CodirRedoCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		curr = view.substr(sublime.Region(0, view.size()))
		buff, delta = history.get_redo(view)

		if delta == 0:
			print ('delta = 0')
			return

		old_to_new = {'additions': {}, 'removals': {}}
		for i, s in enumerate(difflib.ndiff(buff, curr)):
			if s[0] == ' ': continue
			elif s[0] == '-':
				old_to_new['removals'][i] = s[-1]
			elif s[0] == '+':
				old_to_new['additions'][i] = s[-1]

		delta = utils.apply_deltas_to_deltas(old_to_new, delta)
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
		# view = self.view
		# curr = self.view.substr(sublime.Region(0, self.view.size()))
		# buff, delta = history.get_redo(view)
		# if buff == 0 and delta == 0: return

		# old_to_new = {'additions': {}, 'removals': {}}
		# for i, s in enumerate(difflib.ndiff(buff, curr)):
		# 	if s[0] == ' ': continue
		# 	elif s[0] == '-':
		# 		old_to_new['removals'][i] = s[-1] 
		# 	elif s[0] == '+':
		# 		old_to_new['additions'][i] = s[-1]

		# for i in sorted(old_to_new['additions'].keys()):
		# 	for j in reversed(sorted(delta['additions'].keys())):
		# 		if i <= j:
		# 			delta['additions'][j+1] = delta['additions'][j]
		# 			del delta['additions'][j]
		# 	for j in reversed(sorted(delta['removals'].keys())):
		# 		if i <= j:
		# 			delta['removals'][j+1] = delta['removals'][j]
		# 			del delta['removals'][j]

		# for i in sorted(old_to_new['removals'].keys()):
		# 	for j in sorted(delta['removals'].keys()):
		# 		if i < j:
		# 			delta['removals'][j-1] = delta['removals'][j]
		# 			del delta['removals'][j]
		# print(delta['additions'])

		# for i in sorted(delta['additions'].keys()):
		# 	history.insert[view.id()] = [True, True];
		# 	self.view.insert(edit, i, delta['additions'][i])
		# for i in reversed(sorted(delta['removals'].keys())):
		# 	print(i)
		# 	history.insert[view.id()] = [True, True];
		# 	self.view.erase(edit, sublime.Region(i-1, i))

class ApplyDeltasCommand(sublime_plugin.TextCommand):
	def run(self, edit, *args):
		utils.apply_deltas(edit, self.view, args[0])
		