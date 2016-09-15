"use strict";

const net = require("net");

const SERVER_ADDRESS = process.argv[2] || "127.0.0.1";
const SERVER_PORT = process.argv[3] || 7093;

const server = net.createServer()
  .on("connection", socket => {
    console.log("Connected: %j", socket.remoteAddress);
    var buffer = new Buffer(0);
    socket.on("data", chunk => {
      buffer = Buffer.concat([buffer, chunk]);
      console.log("Received: %j", chunk.toString());
      // TODO: Parse JSON.
      socket.write("Server response: " + new Date() + "\n");
      socket.end();
    });
    socket.on("error", err => {
      console.log("Socket error:", err);
    });
  })
  .on("error", err => {
    console.log("Server error:", err.message);
  })
  .listen(SERVER_PORT, SERVER_ADDRESS, (err) => {
    const address = server.address();
    console.log('Listening: %j', address);
    // server.close(); // Shutdowns the server
  });
