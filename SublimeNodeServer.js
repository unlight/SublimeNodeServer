/**
 * SublimeNodeServer.js
 * @flow
 */
'use strict';

const net = require('net');

const SERVER_PORT = process.argv[2] || 7093;

const server = net.createServer()
  .on('connection', socket => {
    console.log('Connected: %j', socket.remoteAddress);
    var buffer = new Buffer(0);
    socket.on('data', chunk => {
      buffer = Buffer.concat([buffer, chunk]);
      console.log('Received: %j', chunk.toString());
      console.log('Buffer: %j', buffer.toString());
    });
    socket.on("error", err => {
      console.log("Socket error:", err);
    });
  })
  .on('error', error => {
    console.log(error);
  })
  .listen(SERVER_PORT, () => {
    const address = server.address();
    console.log('Listening: %j', address);
  });
