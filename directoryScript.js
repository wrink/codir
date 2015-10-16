var socket = io();

var dragging = '';

function newFMU(fd, f, d) {
	return {
		filedir: fd,
		file: f,
		dir: d
	};
}

function getDirectory() {
	return $("meta[name='directory']").attr('content');
}

function drag(e) {
	dragging = e.target.firstChild.id
}

function dragOver(e) {
	e.preventDefault();
}

function dragOverDir(e) {
	if (dragging != e.target.id) {
		e.preventDefault();
		$('#'+ e.target.id).removeClass('glyphicon-folder-close');
		$('#'+ e.target.id).addClass('glyphicon-folder-open');
	}
}

function dragLeave(e) {
	$('#'+ e.target.id).removeClass('glyphicon-folder-open');
	$('#'+ e.target.id).addClass('glyphicon-folder-close');
}

function dropDir(e) {
	e.preventDefault();
	$('#'+ e.target.id).removeClass('glyphicon-folder-open');
	$('#'+ e.target.id).addClass('glyphicon-folder-close');

	var file = dragging;
	dragging = '';

	var directory = getDirectory();

	console.log(e.target.id + " " + file);

	socket.emit('file-move-update', newFMU(directory + '/' + file, file, directory + '/' + e.target.id));
}

function dropBack(e) {
	e.preventDefault();
	var file = dragging;
	dragging = '';

	var directory = getDirectory();

	socket.emit('file-move-update', newFMU(directory + '/' + file, file, directory + '/..'));
}

function dropTrash(e) {
	e.preventDefault();
	var file = dragging;
	dragging = '';

	var directory = getDirectory();

	socket.emit('file-delete-update', directory + '/' + file);
}

function openDir(e) {
	e.preventDefault();
	var directory = getDirectory() + '/' + e.target.id;

	var url = '/directory';
	var form = $('<form class="hidden" action="' + url + '" method="post">' + '<input type="text" name="dir" value="' + directory + '" />' +'</form>');
	$('body').append(form);

	form.submit();
}

function openFile(e) {
	e.preventDefault();
	var directory = getDirectory() + '/' + e.target.id;

	var url = '/file';
	var form = $('<form class="hidden" action="' + url + '" method="post">' + '<input type="text" name="dir" value="' + directory + '" />' +'</form>');
	$('body').append(form);

	form.submit();
}

function openBack(e) {
	e.preventDefault();
	var directory = getDirectory() + '/..';

	var url = '/directory';
	var form = $('<form class="hidden" action="' + url + '" method="post">' + '<input type="text" name="dir" value="' + directory + '" />' +'</form>');
	$('body').append(form);

	form.submit();
}

$(document).ready(function() {
	$('#new-file').on('keydown', function(event) {
		if (event.keyCode == 13) {
			event.preventDefault();
			console.log('return');
			socket.emit('new-file-update', { file: getDirectory() + '/' + this.value, dir: getDirectory() });
		}
	});
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

	var url = '/directory';
	var form = $('<form class="hidden" action="' + url + '" method="post">' + '<input type="text" name="dir" value="' + directory + '" />' +'</form>');
	$('body').append(form);

	form.submit();
});

socket.on('new-file-update', function(update) {
	var directory = getDirectory();

	if (directory === update) {
		var url = '/directory';
		var form = $('<form class="hidden" action="' + url + '" method="post">' + '<input type="text" name="dir" value="' + directory + '" />' +'</form>');
		$('body').append(form);

		form.submit();
	}
});

socket.on('already-exists-error', function() {
	$('#already-exists').removeClass('hidden');
});