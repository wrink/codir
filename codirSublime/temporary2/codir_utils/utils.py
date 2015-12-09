import sublime
from . import history

def remove_deltas_from_deltas(apply_from, apply_to):
	for i in sorted(apply_from['additions'].keys()):
		for j in reversed(sorted(apply_to['additions'].keys())):
			if i <= j:
				apply_to['additions'][j+1] = apply_to['additions'][j]
				del apply_to['additions'][j]
		for j in reversed(sorted(apply_to['removals'].keys())):
			if i <= j:
				apply_to['removals'][j+1] = apply_to['removals'][j]
				del apply_to['removals'][j]
	for i in reversed(sorted(apply_from['removals'].keys())):
		for j in sorted(apply_to['additions'].keys()):
			if i < j:
				apply_to['additions'][j-1] = apply_to['additions'][j]
				del apply_to['additions'][j]
			elif i == j and apply_from['removals'][i] == apply_to['additions'][j]:
				del apply_to['additions'][j]
				for k in sorted(apply_to['additions'].keys()):
					if j < k:
						apply_to['additions'][k-1] = apply_to['additions'][k]
						del apply_to['additions'][k]
				for k in sorted(apply_to['removals'].keys()):
					if j < k:
						apply_to['removals'][k-1] = apply_to['removals'][k]
						del apply_to['removals'][k]
		for j in sorted(apply_to['removals'].keys()):
			if i < j:
				apply_to['removals'][j-1] = apply_to['removals'][j]
				del apply_to['removals'][j]

	return apply_to

def apply_deltas_to_deltas(apply_from, apply_to):
	for i in sorted(apply_from['additions'].keys()):
		for j in reversed(sorted(apply_to['additions'].keys())):
			if i <= j:
				apply_to['additions'][j+1] = apply_to['additions'][j]
				del apply_to['additions'][j]
		for j in reversed(sorted(apply_to['removals'].keys())):
			if i <= j:
				apply_to['removals'][j+1] = apply_to['removals'][j]
				del apply_to['removals'][j]
	for i in reversed(sorted(apply_from['removals'].keys())):
		for j in sorted(apply_to['additions'].keys()):
			if i < j:
				apply_to['additions'][j-1] = apply_to['additions'][j]
				del apply_to['additions'][j]
		for j in sorted(apply_to['removals'].keys()):
			if i < j:
				apply_to['removals'][j-1] = apply_to['removals'][j]
				del apply_to['removals'][j]
			elif i == j and apply_from['removals'][i] == apply_to['removals'][j]:
				del apply_to['removals'][j]
				for k in sorted(apply_to['additions'].keys()):
					if j < k:
						apply_to['additions'][k-1] = apply_to['additions'][k]
						del apply_to['additions'][k]
				for k in sorted(apply_to['removals'].keys()):
					if j < k:
						apply_to['removals'][k-1] = apply_to['removals'][k]
						del apply_to['removals'][k]

	return apply_to

def apply_deltas(edit, view, delta, bit=0):
	for i in sorted(delta['additions'].keys()):
		history.insert[view.id()][bit] = True
		view.insert(edit, i, delta['additions'][i])
	for i in reversed(sorted(delta['removals'].keys())):
		history.insert[view.id()][bit] = True
		view.erase(edit, sublime.Region(i, i+1))

	history.insert[view.id()][bit] = True

def remove_deltas(edit, view, delta, bit=0):
	for i in sorted(delta['removals'].keys()):
		history.insert[view.id()][bit] = True
		view.insert(edit, i, delta['removals'][i])
	for i in reversed(sorted(delta['additions'].keys())):
		history.insert[view.id()][bit] = True
		view.erase(edit, sublime.Region(i, i+1))
