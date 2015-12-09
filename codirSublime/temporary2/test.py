import sublime, sublime_plugin

class PutCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.replace(edit, sublime.Region(0,0), 'a')