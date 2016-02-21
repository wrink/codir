var socket = io();
var Range = ace.require('ace/range').Range;
var markers = [];

var deltas = [0];
var userDeltas = [0];
var deltaBuffer = [];
var historyPointer = 0;

socket.emit('new-page-update', getDirectory());

function getDirectory() {
	return $("meta[name='directory']").attr('content');
}

// function compoundDeltas() {
// 	if (deltaBuffer != []) {
// 		userDeltas.push(deltaBuffer);
// 		deltaBuffer = [];
// 	}
// }

function subtractDeltas(base, negative) {
	//console.log(JSON.stringify(negative))

	for (i=0; i<base.length; i++) {
		if (negative.action == 'insert') {
			if (negative.start.row < base[i].start.row) {
				console.log('i1')
				length = negative.lines.length - 1;
				base[i].start.row += length;
				base[i].end.row += length;
			} else if (negative.start.row == base[i].start.row && negative.start.column <= base[i].start.column && !base[i].undone) {
				console.log('i2')
				vertLength = negative.lines.length - 1;
				horiLength = negative.lines[vertLength].length;

				base[i].start.row += vertLength;
				base[i].end.row += vertLength;
				base[i].start.column += horiLength;// - negative.start.column;
				if (base[i].start.row == base[i].end.row) base[i].end.column += horiLength;// - negative.start.column;
			} else if (base[i].action == 'insert' && base[i].undone == undefined && (negative.start.row < base[i].end.row || (negative.start.row == base[i].end.row && negative.start.column < base[i].end.column))) {
				console.log('i3')
				set = JSON.parse(JSON.stringify([base[i], base[i]]));

				vertLength = negative.lines.length - 1;
				horiLength = negative.lines[vertLength].length;
				rowCenter = 1 + negative.start.row - set[0].start.row;
				columnCenter = negative.start.column;

				set[0].end.row = negative.start.row;
				set[0].end.column = negative.start.column;
				set[0].lines.splice(rowCenter, set[0].lines.length - rowCenter);
				set[0].lines[set[0].lines.length - 1] = set[0].lines[set[0].lines.length - 1].substr(0, columnCenter);

				set[1].start.row = negative.end.row;
				set[1].end.row = negative.end.row + vertLength;
				set[1].start.column = negative.end.column;
				if (set[1].start.row == set[1].end.row) set[1].end.column += horiLength;
				set[1].lines.splice(0, rowCenter - 1);
				set[1].lines[0] = set[1].lines[0].substr(columnCenter);

				base.splice.apply(base, [i, 1].concat(set)); 
			} else if (base[i].action == 'insert' && base[i].undone && base[i].start.row == negative.start.row && base[i].start.column == negative.start.column) {
				console.log('i4')
				var baseStr = '';
				var negativeStr = '';

				for (j in base[i].lines) baseStr += base[i].lines[j];
				for (j in negative.lines) negativeStr += negative.lines[j];

				start = baseStr.indexOf(negativeStr);

				if (start >= 0) {
					set = JSON.parse(JSON.stringify([base[i], base[i], base[i]]));
					console.log('Start: '+baseStr)
					distToStart = start;
					distToEnd = start + negativeStr.length;
					startRow = false;
					for (var j = 0; j < base[i].lines.length; j++) {
						if (base[i].lines[j].length < distToStart && !startRow){
							distToStart -= base[i].lines[j].length;
						} else if (base[i].lines[j].length >= distToStart && !startRow) {
							set[0].end.row = set[0].start.row + j;
							set[0].end.column = (j == 0)? set[0].start.column + distToStart : distToStart;
							set[0].lines.splice(j+1, base[i].lines.length - (j+1));
							set[0].lines[j] = set[0].lines[j].substr(0, distToStart - ((set[0].lines.length == 1) ? set[0].start.column : 0));

							set[1].start.row = set[0].end.row;
							set[1].start.column = set[0].end.column;
							set[1].lines.splice(0, j);
							set[1].lines[0] = set[1].lines[0].substr(distToStart);

							startRow = j;
						}

						if (base[i].lines[j].length < distToEnd) {
							distToEnd -= base[i].lines[j].length;
						} else if (base[i].lines[j].length >= distToEnd) {
							set[1].end.row = set[0].start.row + j;
							set[1].end.column = (set[1].lines.length == 1)? distToEnd + set[1].start.column : distToEnd;
							set[1].lines.splice(1 + j - startRow, set[1].lines.length - (1 + j - startRow));
							set[1].lines[set[1].lines.length-1] = set[1].lines[set[1].lines.length-1].substr(0, distToEnd);

							set[2].start.row = set[1].end.row;
							set[2].start.column = set[1].end.column;
							set[2].lines.splice(0, j - set[1].lines.length - 1);
							set[2].lines[0] = set[2].lines[0].substr(distToEnd);
							console.log('test')
							break;
						}
					}

					set[1].undone = undefined;
					
					console.log('test: ' + JSON.stringify(set));
					
					negative.lines.splice(0, set[1].lines.length-1);
					negative.lines[0] = negative.lines[0].substr(set[1].lines[set[1].lines.length-1].length);
					negative.start.row = set[1].end.row;
					negative.start.column = set[1].end.column;

					if (set[2].lines.length == 1 && set[2].lines[0] == '') set.splice(2,1);
					if (set[0].lines.length == 1 && set[0].lines[0] == '') set.splice(0,1);
					
					i += set.length-1;

					base.splice.apply(base, [i, 1].concat(set));
				}
			}
		} else {
			if (negative.end.row < base[i].start.row) {
				console.log('r1')
				length = negative.lines.length - 1;
				base[i].start.row -= length;
				base[i].end.row -= length;
			} else if (negative.end.row == base[i].start.row && negative.end.column <= base[i].start.column) {
				console.log('r2')
				vertLength = negative.lines.length - 1;
				horiLength = negative.lines[vertLength].length

				base[i].start.row -= vertLength;
				base[i].end.row -= vertLength;
				base[i].start.column -= (vertLength == 0) ? horiLength : horiLength - negative.start.column;
				if (base[i].start.row == base[i].end.row) base[i].end.column -= (vertLength == 0) ? horiLength : horiLength - negative.start.column;
			} else if (negative.start.row > base[i].end.row || negative.start.column >= base[i].end.column) {
				console.log('r3')
				continue;
			} else {
				console.log('r4')
				insideStart = (negative.start.row > base[i].start.row || (negative.start.row == base[i].start.row && negative.start.column > base[i].start.column));
				insideEnd = (negative.end.row < base[i].end.row || (negative.end.row == base[i].end.row && negative.end.column < base[i].end.column));

				vertLength = negative.lines.length - 1;
				horiLength = negative.lines[vertLength].length;

				if (base[i].action == 'insert')
				{
					rowCenter = negative.start.row - base[0].start.row;
					columnCenter = negative.start.column;

					if (insideStart && insideEnd) {
						console.log('r4.1')

						set = JSON.parse(JSON.stringify([base[i], base[i], base[i]]));
						console.log('set: '+ JSON.stringify(set))

						set[0].end.row = negative.start.row;
						set[0].end.column = negative.start.column;
						set[0].lines.splice(rowCenter+1, set[0].lines.length - (rowCenter+1));  //(rowCenter, set[0].lines.length - rowCenter);
						set[0].lines[set[0].lines.length -1] = set[0].lines[set[0].lines.length -1].substr(0, columnCenter-1);

						set[2].start.row = negative.end.row;
						set[2].start.column = negative.end.column;
						set[2].lines.splice(0, rowCenter);
						set[2].lines[0] = set[2].lines[0].substr(negative.end.column-1);
						// set[2].end.row -= vertLength;
						// if (negative.end.row == base[i].end.row) set[2].end.column -= horiLength;


						set[1].start.row = set[0].end.row;
						set[1].start.column = set[0].end.column;
						set[1].end.row = negative.end.row;
						set[1].end.column = negative.end.column;
						set[1].lines.splice(0, set[0].lines.length-1);
						set[1].lines.splice(1 + set[1].end.row - set[1].start.row, set[1].lines.length - (1 + set[1].end.row - set[1].start.row));
						set[1].lines[set[1].lines.length-1] = set[1].lines[set[1].lines.length-1].substr(0, set[1].lines[set[1].lines.length-1].length - set[2].lines[0].length);
						set[1].lines[0] = set[1].lines[0].substr(set[0].lines[set[0].lines.length-1].length);
						set[1].undone = true;

						base.splice.apply(base, [i, 1].concat(set));
						i += 2;
					} else if (insideStart) {
						console.log('r4.2')
						set = JSON.parse(JSON.stringify([base[i], base[i]]));

						set[0].end.row = negative.start.row;
						set[0].end.column = negative.start.column;
						set[0].lines.splice(rowCenter, base[i].lines.length - rowCenter);
						set[0].lines[base[i].lines.length -1] = base[i].lines[base[i].lines.length -1].substr(0, columnCenter);  //(columnCenter);

						set[1].start.row = negative.start.row;
						set[1].start.column = negative.start.column;
						set[1].lines.splice(0, rowCenter);
						set[1].lines[0] = set[0].lines[0].substr(columnCenter);
						set[1].undone = true;

						base.splice.apply(base, [i, 1].concat(set));
						i++;

					} else if (insideEnd) {
						console.log('r4.3')
						sameEndRow = negative.end.row == base[i].end.row

						set = JSON.parse(JSON.stringify([base[i], base[i]]));

						set[1].start.row = negative.start.row;
						set[1].start.column = negative.start.column;
						set[1].lines.splice(0, rowCenter);
						set[1].lines[0] = base[i].lines[0].substr(negative.end.column - base[i].start.column);
						set[1].end.row -= vertLength;
						if (sameEndRow) set[1].end.column -= horiLength;

						set[0].end.row = set[1].start.row;
						set[0].end.column = set[1].start.column;
						set[0].lines.splice(rowCenter+1, set[1].lines.length - (rowCenter+1));
						set[0].lines[rowCenter] = set[0].lines[rowCenter].substr(0, set[0].lines[rowCenter].length - set[1].lines[0].length);
						set[0].undone = true;

						base.splice.apply(base, [i, 1].concat(set));
						i++;
					} else {
						console.log('r4.4')
						base[i].undone = true;
					}
				} else {
					console.log('r4.5')
					if (insideStart) {
						continue;
					} else {
						rowOffset = base[i].start.row - negative.start.row;
						columnOffset = (base[i].lines.length == 1) ? 0 : negative.start.column + base[i].lines[0].length;

						base[i].start.row = negative.start.row;
						base[i].start.column = negative.start.column;
						base[i].end.row -= rowOffset;
						base[i].end.column = columnOffset;
					}
				}
			}
		}
	}
	//console.log(base)
	return base;
}

// function historyEdit(editor, isUndo) {
// 	var isUndo=
// 	delta = userDeltas[historyPointer];
	
// 	if ((isUndo && historyPointer == 0) || (!isUndo && historyPointer == userDeltas.length - 1)) return;

// 	(isUndo) ? historyPointer-- : historyPointer++;

// 	for (i = 1 + delta.pointer; i < deltas.length; i++) {
// 		delta.delta = subtractDeltas([delta.delta], deltas[i]);
// 	}

// 	if (isUndo) {
// 		delta.delta.action = (delta.delta.action == 'insert') ? 'remove' : 'insert';
// 	}

// 	preUpdateFlag = true;
// 	editor.session.getDocument().applyDeltas([delta.delta]);
// }

var EditorUpdate = function(event, html) {
	this.event = event;
	this.html = html;
	this.file = getDirectory();
	this.id = socket.id;
}
var ChangeSelectUpdate = function(ranges, path) {
	this.ranges = ranges;
	this.path = path;
}

$(document).ready(function() {
	console.log(document.location.pathname);
	var editor = ace.edit('editor');
	editor.setTheme("ace/theme/idle_fingers");

	var Undo = function() {
		console.log('Undo')
		delta = JSON.parse(JSON.stringify(userDeltas[historyPointer]));

		if (historyPointer == 0) return;
		else historyPointer--;

		console.log(JSON.stringify(deltas))

		for (var i = 1 + delta.pointer; i < deltas.length; i++) {
			delta.delta = subtractDeltas(delta.delta, deltas[i]);
			console.log(JSON.stringify(deltas[i]))
			console.log(JSON.stringify(delta.delta))
		}

		for (var i = 0; i < delta.delta.length; i++) {
			if (delta.delta[i].undone) {
				delta.delta.splice(i, 1);
				i--;
			} else delta.delta[i].action = (delta.delta[i].action == 'insert') ? 'remove' : 'insert';
		}

		for (var i = delta.delta.length-1; i >= 0; i--) {
			preUpdateFlag = true;
			editor.session.getDocument().applyDeltas([delta.delta[i]]);
		}
	}

	var Redo = function() {
		console.log('Redo')

		if (historyPointer == userDeltas.length - 1) return;
		else historyPointer++;

		delta = userDeltas[historyPointer];
		
		for (i = 1 + delta.pointer; i < deltas.length; i++) {
			delta.delta = subtractDeltas([delta.delta], deltas[i]);
		}

		for (var i = 0; i < delta.delta.length; i++) {
			preUpdateFlag = true;
			editor.session.getDocument().applyDeltas([delta.delta[i]]);
		}
	}

	editor.commands.addCommand({
		name: 'Undo',
		exec: Undo,
		bindKey: {mac: 'cmd-z', win: 'ctrl-z'}
	});
	editor.commands.addCommand({
		name: 'Redo',
		exec: Redo,
		bindKey: {mac: 'cmd-shift-z', win: 'ctrl-shift-z'}
	});
	editor.$blockScrolling = Infinity;

	var preUpdateFlag = true;

	editor.on('change', function(event) {
		deltas.push(event);

		if (preUpdateFlag) {
			preUpdateFlag = false;
		}
		else {
			console.log(event);
			//deltaBuffer.push({'delta': event, 'pointer': deltas.length - 1});
			historyPointer++;

			if (historyPointer < userDeltas.length) userDeltas.splice(historyPointer, userDeltas.length - historyPointer);

			userDeltas.push({'delta': [event], 'pointer': deltas.length - 1});
			console.log(userDeltas[userDeltas.length-1].delta[0])
			
			socket.emit('editor-update', new EditorUpdate(event, editor.getValue()));
		}
	});

	editor.selection.on('changeSelection', function() {
		socket.emit('change-select-update', new ChangeSelectUpdate(editor.getSelection().getAllRanges(), getDirectory()));
	})

	socket.on('new-page-update', function(update) {
		if (update.text.length == 0) preUpdateFlag = false;
		editor.setValue(update.text);

		if(update.text != '') {
			for (var i in update.cursors) {
				var index = 0;
				for (var j in update.cursors[i]) {
					if (j != socket.id && update.cursors[i][j]) {
						var mark = new Range(update.cursors[i][j].start.row, update.cursors[i][j].start.column, update.cursors[i][j].end.row, update.cursors[i][j].column);
						markers.push(editor.getSession().addMarker(mark, "other-user-" + (index % 5), "text", false));
						(index % 5)
						index++;
					}
				}
			}
		}
	});

	socket.on('change-select-update', function(update) {

		for (var i = 0; i < markers.length; i++) {
			editor.getSession().removeMarker(markers[i]);
		}

		markers = [];

		var index = 0;
		for (var i in update) {
			for (var j in update[i]) {
				var mark = new Range(update[i][j].start.row, update[i][j].start.column, update[i][j].end.row, update[i][j].end.column);
				if (i != socket.id) {
					markers.push(editor.getSession().addMarker(mark, "other-user-" + (index % 5), "text", false));
					console.log(index % 5);
				}
			}
			index++;
		}
	});

	socket.on('editor-update', function(update) {
		if (update.file === getDirectory() && update.id != socket.id) {
			preUpdateFlag = true;
			editor.session.getDocument().applyDeltas([update.event]);
		}
	});

	socket.on('file-move-update', function(update) {
		var directory = getDirectory();

		if (update.filedir === directory) {
			alert("Warning: this directory has been moved to " + update.newFileDir);
			$("meta[name='directory']")[0].content = update.newFileDir;
		} else if (directory.indexOf(update.filedir) > -1) {
			alert("Warning: a parent of this directory has been moved to " + update.newFileDir);
			$("meta[name='directory']")[0].content = update.newFileDir;
		}
		var directory = getDirectory();

		var url = '/directory';
		var form = $('<form class="hidden" action="' + url + '" method="post">' + '<input type="text" name="dir" value="' + directory + '" />' +'</form>');
		$('body').append(form);

		form.submit();
	});

	socket.on('file-delete-update', function(update) {
		var directory = getDirectory();

		if (directory === update || directory.indexOf(update) > -1) {
			alert("Warning: this directory has been unlinked");
			window.location.replace('/');
		}
	});
});