import sublime, sublime_plugin
import time, difflib

from sublime import Region

global history_counter
global buffer_history
global edit_history
global insert
global unapplied_deltas

history_counter = {}
buffer_history = {}
edit_history = {}
insert = {}
unapplied_deltas = {}

def millis():
	return int(round(time.time() * 1000))

def init_view(view):
	t = millis()
	id = view.id()

	history_counter[id] = t
	buffer_history[id] = {}
	buffer_history[id][t] = view.substr(sublime.Region(0, view.size()))
	edit_history[id] = {}
	edit_history[id][t] = {'additions': {}, 'removals': {}}
	insert[id] = [False, False]

def push_history(view):
	t = millis()
	id = view.id()
	if id not in buffer_history: init_view(view)

	deltas = get_deltas(view)

	keys = sorted(edit_history[id].keys())
	for key in keys:
		if key > history_counter[id]:
			del edit_history[id][key]
	if deltas == {'additions': {}, 'removals': {}}: return

	history_counter[id] = t
	edit_history[id][t] = deltas
	buffer_history[id][t] = view.substr(sublime.Region(0, view.size()))

def get_undo(view):
	id = view.id()
	counter = history_counter[id]
	keys = sorted(edit_history[id].keys())
	try:
		index = keys.index(counter)
	except:
		return (0, 0)

	if len(keys) > 1 and index > 0:
		history_counter[id] = keys[index-1]
		return (buffer_history[id][keys[index]], edit_history[id][keys[index]])
	else:
		return (0, 0)[keys[index]], edit_history[id][keys[index]])

def get_redo(view):
	id =  view.id()
	counter =  history_counter[id]
	keys = sorted(edit_history[id].keys())
	try:
		index = keys.index(counter)
	except:
		return (0, 0)

	if len(keys) > 1 and index < len(keys) - 1:
		history_counter[id] = keys[index+1]
		return (buffer_history[id][keys[index]], edit_history[id][keys[index+1]])
	else:
		return (0, 0)
def is_insert(view, external_bit=0):
	t =  millis()
	id = view.id()
	if id not in buffer_history:
		init_view(view)

	if insert[id][external_bit]:
		insert[id][external_bit] = False
		return True
	else: return False

def get_deltas(view):
	id = view.id()

	curr = view.substr(sublime.Region(0, view.size()))
	deltas = {'additions': {}, 'removals': {}}
	for i, s in enumerate(difflib.ndiff(buffer_history[id][history_counter[id]], curr)):
		if s[0] == ' ': continue
		elif s[0] == '-':
			deltas['removals'][i] = s[-1] 
		elif s[0] == '+':
			deltas['additions'][i] = s[-1]

	return deltas