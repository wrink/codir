import sublime, sublime_plugin
import difflib
from datetime import datetime
from sublime import Region

global history_counter
global buffer_history
global edit_history
global insert
global delta_queue

history_counter = {}
buffer_history = {}
edit_history = {}
insert = {}
delta_queue = {}

def millis():
	return (0.1 + datetime.now().microsecond) / 1000

def init_view(view):
	t = millis()
	id = view.id()

	history_counter[id] = t
	buffer_history[id] = {}
	buffer_history[id][t] = view.substr(sublime.Region(0, view.size()))
	edit_history[id] = {}
	edit_history[id][t] = {'additions': {}, 'removals': {}}
	insert[id] = [False, False]
	delta_queue[id] = []

def push_history(view):
	print ('push_history')
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
		print ('index-1')
		return (0, 0)

	if len(keys) >= 1 and index > 0:
		history_counter[id] = keys[index-1]
		return (buffer_history[id][keys[index]], edit_history[id][keys[index]])
	elif len(keys) >= 1 and index == 0:
		history_counter[id] = -1
		return (buffer_history[id][keys[index]], edit_history[id][keys[index]])
	else:
		print (keys)
		print (str(counter) + ' ' +  str(index))
		return (0, 0)

def get_redo(view):
	id =  view.id()
	counter =  history_counter[id]
	keys = sorted(edit_history[id].keys())
	try:
		index = keys.index(counter)
	except:
		if counter == -1:
			index = -1
		else:
			print ('ERROR: index ' + index + ' does not exist')

	if len(keys) >= 1 and index < len(keys) - 1:
		history_counter[id] = keys[index+1]
		return (buffer_history[id][keys[index]], edit_history[id][keys[index+1]])
	# elif len(keys) >= 1 and index == len(keys) - 1:
	# 	history_counter[id] = -1
	# 	return (buffer_history[id][keys[index]], edit_history[id][keys[index+1]])
	elif len(keys) >= 1 and index == -1:
		history_counter[id] = keys[0]
		key =  sorted(buffer_history[id].keys())[0]
		return(buffer_history[id][key], edit_history[id][keys[0]])
	else:
		print (len(keys))
		print (index)
		return (0, 0)
def is_insert(view, external_bit=0):
	t =  millis()
	id = view.id()
	if id not in buffer_history:
		init_view(view)

	if insert[id][external_bit]:
		insert[id][external_bit] = False
		print ('is_insert')
		return True
	else: return False

def get_deltas(view):
	id = view.id()

	curr = view.substr(sublime.Region(0, view.size()))
	deltas = {'additions': {}, 'removals': {}}
	counter = history_counter[id]
	if counter == -1:
		# print(buffer_history[id])
		counter = sorted(buffer_history[id].keys())[0]
	for i, s in enumerate(difflib.ndiff(buffer_history[id][counter], curr)):
		if s[0] == ' ': continue
		elif s[0] == '-':
			deltas['removals'][i] = s[-1] 
		elif s[0] == '+':
			deltas['additions'][i] = s[-1]

	return deltas