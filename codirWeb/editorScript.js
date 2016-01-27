var socket = io();
var Range = ace.require('ace/range').Range;
var markers = [];

socket.emit('new-page-update', getDirectory());

function getDirectory() {
	return $("meta[name='directory']").attr('content');
}

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
	editor.$blockScrolling = Infinity;

	var preUpdateFlag = true;

	editor.on('change', function(event) {
		if (preUpdateFlag) {
			preUpdateFlag = false;
		}
		else {
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