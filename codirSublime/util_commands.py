import sublime, sublime_plugin
import difflib
from . import history
from . import codir_client as client

class ApplyDeltasCommand(sublime_plugin.TextCommand):
	def run(self, edit, deltas):
		additions = {int(i): deltas['additions'][i] for i in deltas['additions']}
		removals = {int(i): deltas['removals'][i] for i in deltas['removals']}
		for i in sorted(additions.keys()):
			history.delta[self.view.id()] = True
			self.view.insert(edit, int(i), additions[i])
		for i in reversed(sorted(removals.keys())):
			history.delta[self.view.id()] = True
			if self.view.substr(sublime.Region(i, i+1)) == removals[i]:
				self.view.erase(edit, sublime.Region(int(i), int(i)+1))
		history.buffer_history[self.view.id()].append(self.view.substr(sublime.Region(0, self.view.size())))

class CodirUndoCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		id = self.view.id()

		deltas = {'additions': {}, 'removals': {}, 'pointer': len(history.buffer_history[id])-1}

		for i, s in enumerate(difflib.ndiff(history.buffer_history[id][history.delta_history[id][history.history_pointer[id]]['pointer']], history.buffer_history[id][-1])):
			if s[0] == ' ': continue
			elif s[0] == '-':
				deltas['removals'][i] = s[-1] 
			elif s[0] == '+':
				deltas['additions'][i] = s[-1]

		deltas = history.subtract_undos(history.delta_history[id][history.history_pointer[id]], deltas)

		if history.history_pointer[id]:
			print ('step back')
			history.history_pointer[id] -= 1
		
		additions = {int(i): deltas['additions'][i] for i in deltas['additions']}
		removals = {int(i): deltas['removals'][i] for i in deltas['removals']}

		for i in sorted(removals.keys()):
			history.delta[self.view.id()] = True
			self.view.insert(edit, int(i), removals[i])
		for i in reversed(sorted(additions.keys())):
			history.delta[self.view.id()] = True
			if self.view.substr(sublime.Region(i, i+1)) == additions[i]:
				self.view.erase(edit, sublime.Region(int(i), int(i)+1))

		history.buffer_history[id].append(self.view.substr(sublime.Region(0, self.view.size())))

		rem = deltas['additions']
		add = deltas['removals']
		deltas['removals'] = rem
		deltas['additions'] = add

		path = 'codirSublime/projects/'
		socket = client.sockets[self.view.window().id()]
		file = self.view.file_name()
		path_start = file.index(path) + len(path + socket['shareid'] + '/')
		socket['socket'].emit('workspace-file-edit-update', {'path': file[path_start:], 'deltas': deltas, 'shareid': socket['shareid']})

class CodirRedoCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		id = self.view.id()

		deltas = {'additions': {}, 'removals': {}, 'pointer': len(history.buffer_history[id])-1}

		for i, s in enumerate(difflib.ndiff(history.buffer_history[id][history.delta_history[id][history.history_pointer[id]+1]['pointer']], history.buffer_history[id][-1])):
			if s[0] == ' ': continue
			elif s[0] == '-':
				deltas['removals'][i] = s[-1] 
			elif s[0] == '+':
				deltas['additions'][i] = s[-1]

		deltas = history.subtract_redos(history.delta_history[id][history.history_pointer[id]], deltas)

		if history.history_pointer[id]:
			history.history_pointer[id] += 1
		
		additions = {int(i): deltas['additions'][i] for i in deltas['additions']}
		removals = {int(i): deltas['removals'][i] for i in deltas['removals']}

		for i in sorted(additions.keys()):
			history.delta[self.view.id()] = True
			self.view.insert(edit, int(i), removals[i])
		for i in reversed(sorted(removals.keys())):
			history.delta[self.view.id()] = True
			if self.view.substr(sublime.Region(i, i+1)) == additions[i]:
				self.view.erase(edit, sublime.Region(int(i), int(i)+1))

		history.buffer_history[id].append(self.view.substr(sublime.Region(0, self.view.size())))

		path = 'codirSublime/projects/'
		socket = client.sockets[self.view.window().id()]
		file = self.view.file_name()
		path_start = file.index(path) + len(path + socket['shareid'] + '/')
		socket['socket'].emit('workspace-file-edit-update', {'path': file[path_start:], 'deltas': deltas, 'shareid': socket['shareid']})
