var Mutex = function () {
	this.locked = false;
}

Mutex.prototype = Object.create(Object.prototype);

Mutex.prototype.constructor = Mutex;

Mutex.prototype.acquire = function () {
	while (this.locked);

	this.locked = true;
}

Mutex.prototype.release = function () {
	this.locked = false;
}

Mutex.prototype.acquireAsync = function (callback) {
	setTimeout(function() {
		while (this.locked);

		this.locked = true;

		callback(Mutex.prototype.release);
	}, 0);
}