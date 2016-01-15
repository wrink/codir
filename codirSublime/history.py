import sublime
import difflib

global buffer_history
global delta
global delta_history
global history_pointer

buffer_history = {}
delta = {}
delta_history = {}
history_pointer = {}

def init_view(view):
	id = view.id()
	if id not in buffer_history:
		buffer_history[view.id()] = [view.substr(sublime.Region(0, view.size()))]
		delta[view.id()] = False
		delta_history[view.id()] = [{ 'additions': {}, 'removals': {}, 'pointer': 0}]
		history_pointer[view.id()] = 0

def is_delta(view):
	id = view.id()
	init_view(view)

	if delta[id]:
		delta[id] = False
		return True
	else: return False

def get_deltas(view):
	id = view.id()

	deltas = {'additions': {}, 'removals': {}, 'pointer': len(buffer_history[id])-1}

	for i, s in enumerate(difflib.ndiff(buffer_history[id][-2], buffer_history[id][-1])):
		if s[0] == ' ': continue
		elif s[0] == '-':
			deltas['removals'][i] = s[-1] 
		elif s[0] == '+':
			deltas['additions'][i] = s[-1]
	print (deltas)
	return deltas

def subtract_undos(prev, curr):

	deltas = prev
	deltas['pointer'] = curr['pointer']

	print ('subtracting')
	print (curr)
	print ('from')
	print (prev)

	for i in sorted(curr['additions'].keys()):
		for j in reversed(sorted(prev['additions'].keys())):
			if j>=i:
				deltas['additions'][j+1] = deltas['additions'][j]
				del deltas['additions'][j]
		for j in reversed(sorted(prev['removals'].keys())):
			if j>=i:
				deltas['removals'][j+1] = deltas['removals'][j]
				del deltas['removals'][j]
	for i in reversed(sorted(curr['removals'].keys())):
		for j in sorted(prev['additions'].keys()):
			if j>i:
				deltas['additions'][j-1] = deltas['additions'][j]
				del deltas['additions'][j]
			elif j==1:
				print('removed')
				print(str(j)+':'+deltas['additions'][j])
				del deltas['additions'][j]
		for j in sorted(prev['removals'].keys()):
			if j>=i:
				deltas['removals'][j-1] = deltas['removals'][j]
				del deltas['removals'][j]

	return deltas

def subtract_redos(prev, curr):

	deltas = prev
	deltas['pointer'] = curr['pointer']

	for i in sorted(curr['additions'].keys()):
		for j in reversed(sorted(prev['additions'].keys())):
			if j>=i:
				deltas['additions'][j+1] = deltas['additions'][j]
				del deltas['additions'][j]
		for j in reversed(sorted(prev['removals'].keys())):
			if j>=i:
				deltas['removals'][j+1] = deltas['removals'][j]
				del deltas['removals'][j]
	for i in reversed(sorted(curr['removals'].keys())):
		for j in sorted(prev['additions'].keys()):
			if j>=i:
				deltas['additions'][j-1] = deltas['additions'][j]
				del deltas['additions'][j]
		for j in sorted(prev['removals'].keys()):
			if j>i:
				deltas['removals'][j-1] = deltas['removals'][j]
				del deltas['removals'][j]
			elif j==1:
				del deltas['removals'][j]

	return deltas