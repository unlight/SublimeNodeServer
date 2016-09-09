"use strict";
var net = require("net");

const SERVER_PORT = process.argv[2] || 7093;

var client = new net.Socket();
client.connect(7093, '127.0.0.1');
client.on("connect", () => {
	console.log('Connected to server.');
	client.write('Hello, server! from Client.');
});

client.on("data", buffer => {
	console.log('Received: ' + buffer);
	client.destroy();
});

client.on("error", err => {
	console.log("Error: %j", err);
});

client.on("close", function() {
	console.log('Connection closed');
});