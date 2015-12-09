import sublime, sublime_plugin
from . import history

class ApplyDeltasCommand(sublime_plugin.TextCommand):
	def run(self, edit, deltas):
		additions = deltas['additions']
		removals = deltas['removals']
		for i in sorted(additions.keys()):
			history.delta[self.view.id()] = True
			self.view.insert(edit, int(i), additions[i])
		for i in reversed(sorted(removals.keys())):
			history.delta[self.view.id()] = True
			self.view.erase(edit, sublime.Region(int(i), int(i)+1))
		history.buffer_history[self.view.id()].append(self.view.substr(0, self.view.size()))