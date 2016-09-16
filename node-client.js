"use strict";
var net = require("net");
// Test node client.
const SERVER_PORT = process.argv[2] || 7093;

var client = new net.Socket();
client.connect(SERVER_PORT, "127.0.0.1");
client.on("connect", () => {
	console.log("Connected to server");
	// client.write("Hello, server! from Client.");
	// client.write(JSON.stringify({command: "ping"}));
	// client.write(JSON.stringify({command: "shutdown"}));
	client.write(JSON.stringify({command: "setup"}));
});

client.on("data", buffer => {
	var data = buffer.toString();
	console.log("Server response:");
	console.log(data);
});

client.on("error", err => {
	console.log("Error: %j", err);
});

client.on("close", function() {
	console.log("Connection closed");
});