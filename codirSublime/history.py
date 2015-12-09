import sublime
import difflib

global buffer_history
global delta

buffer_history = {}
delta = {}

def init_view(view):
	id = view.id()
	if id not in buffer_history:
		buffer_history[view.id()] = [view.substr(sublime.Region(0, view.size()))]
	if id not in delta:
		delta[view.id()] = False

def is_delta(view):
	id = view.id()
	init_view(view)

	if delta[id]:
		delta[id] = False
		return True
	else: return False

def get_deltas(view):
	id = view.id()

	deltas = {'additions': {}, 'removals': {}}

	for i, s in enumerate(difflib.ndiff(buffer_history[id][-2], buffer_history[id][-1])):
		if s[0] == ' ': continue
		elif s[0] == '-':
			deltas['removals'][i] = s[-1] 
		elif s[0] == '+':
			deltas['additions'][i] = s[-1]

	return deltas