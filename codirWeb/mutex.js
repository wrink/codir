var Mutex = function () {
	this.lock = false;

	this.aquire = function (callback) {
		var release = function () {
			this.lock = false;
		}

		setTimeout(function () {

			while (this.lock) {};
			this.lock = true;

			callback(release);
		}, 0);
	}
}