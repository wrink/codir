var express = require('express');
var app = express();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var fs = require('fs');
var request = require('request');
var bodyParser = require('body-parser');
var upload = require('multer')();
var path = require('path');
var rmdir = require('rimraf');
var mkdir = require('mkdirp');

var cursors = {};

var isFile = /.*\.[a-zA-Z0-9]+/i;

var NewPageUpdate = function(text, path) {
	this.text = text;
	if(!cursors[path]) cursors[path] = {};
	this.cursors = cursors[path];
}

var GetAddress = function() {
	var os = require('os');
	var ifaces = os.networkInterfaces()

	for (i in ifaces) {
		for (j in ifaces[i]) {
			if (ifaces[i][j].family === 'IPv4' && ifaces[i][j].internal === false) {
				return ifaces[i][j].address;
			} 
		}
	}

	return false;
}

app.use(express.static(__dirname));
app.use(bodyParser.json()); // for parsing application/json
app.use(bodyParser.urlencoded({ extended: true })); // for parsing application/x-www-form-urlencoded
app.set('view engine', 'jade');

app.all('/', function(req, res) {
	var directory = process.env[(process.platform == 'win32') ? 'USERPROFILE' : 'HOME'];
	console.log(directory)
	fs.readdir(directory, function(err, files) {
		if(err) {
			console.log(err);
			return;
		}

		var content = { back: {isBack: true, name: 'Back'} };

		files.forEach(function(file) {
			content[file] = {name: file};
			if(isFile.test(file)) content[file].isFile = true;
			else content[file].isDir = true;
		});

		content["new"] = { isNew: true, name: 'New File'};
		content["trash"] = {isTrash: true, name: 'Trash'};

		res.render('directory.jade', {
			dir: directory,
			contents: content
		});
	});
});
app.post('/directory', upload.array(), function(req, res) {
	var directory = req.body.dir;
	fs.readdir(directory, function(err, files) {
		if(err) {
			console.log(err);
			return;
		}

		var content = { back: {isBack: true, name: 'Back'} };

		files.forEach(function(file) {
			content[file] = {name: file};
			if(isFile.test(file)) content[file].isFile = true;
			else content[file].isDir = true;
		});

		content["new"] = { isNew: true, name: 'New File'};
		content["trash"] = {isTrash: true, name: 'Trash'};

		res.render('directory.jade', {
			dir: directory,
			contents: content
		});
	});
});
app.post('/file', upload.array(), function(req, res) {
	res.render('editor.jade', {
		dir: req.body.dir
	});
});

io.on('connection', function(socket) {
	console.log('a user connected: ', socket.id);
	var file = '';

	socket.on('disconnect', function() {
		console.log('user disconnected: ', socket.id);
		if(cursors[file]){
			if (cursors[file][socket.id]) {
				cursors[file][socket.id] = undefined;
			}
			socket[file] = undefined;
		}
	});

	socket.on('new-page-update', function(update) {
		var text ='';
		file = update;
		console.log(cursors[file]);
		fs.readFile(file, function(err, data) {
			if (err) {
				text = '';
				console.log(err);
			}
			else text = data.toString('utf8');

			fs.writeFileSync(file, text);
			io.to(socket.id).emit('new-page-update', new NewPageUpdate(text, update));
		});
	});

	socket.on('editor-update', function(update) {
		fs.writeFileSync(update.file, update.html);
		io.emit ('editor-update', update);
	});

	socket.on('change-select-update', function(update) {
		cursors[update.path][socket.id] = update.ranges;
		io.emit('change-select-update', cursors[update.path]);
	});

	socket.on('file-move-update', function(update) {
		console.log(typeof update.filedir + " " + typeof update.file);
		cursors[update.dir + '/' + update.file] = cursors[file];
		cursors[file] = undefined;
		file = update.dir + '/' + update.file;
		fs.rename(update.filedir, update.dir + '/' + update.file, function(err, stats) {
			if (err) throw err;
			update.newFileDir = update.filedir, update.dir + '/' + update.file;

			io.emit('file-move-update', update);
		});
	});

	socket.on('file-delete-update', function(update) {
		rmdir(path.normalize(update), function(err) {
			console.log(err);
			io.emit('file-delete-update', update);
		});
	});

	socket.on('new-file-update', function(update) {
		fs.stat(update.file, function(err){
			if (err) {
				if (isFile.test(update.file)) {
					fs.writeFile(update.file, '', function(err) {
						if (err) console.log(err);
						io.emit('new-file-update', update.dir);
					});
				} else {
					mkdir(update.file, function(err) {
						if (err) console.log(err);
						io.emit('new-file-update', update.dir);
					});
				}
			} else {
				io.to(socket.id).emit('already-exists-error');
				console.log('error');
			}
		});
	});	
});

http.listen(3000, '0.0.0.0', function() {
	var addr = GetAddress();

	if (address) console.log('listening to '+GetAddress()+':3000');
	else {
		console.log ('ERROR: no external IPv4 address found!');
		process.exit();
	}
});
