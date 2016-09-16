"use strict";

const net = require("net");
const get = require("lodash.get");
const child_process = require("child_process");
const path = require("path");

const SERVER_ADDRESS = process.argv[2] || "127.0.0.1";
const SERVER_PORT = process.argv[3] || 7093;

const server = net.createServer()
    .on("connection", socket => {
        socket.on("data", chunk => {
            try {
                var payload = JSON.parse(chunk.toString());    
            } catch (err) {
                return socket.emit("error", err);
            }
            console.log("Incoming message: %j", payload);
            payload.socket = socket;
            payload.server = server;
            var cmd = get(payload, "command");
            console.log("Command: " + cmd);
            var func = get(commands, cmd, (payload, callback) => callback());
            func(payload, (err, response) => {
                if (err) return socket.emit("error", err);
                console.log("Responding: %j", response);
                if (response) {
                    socket.write(JSON.stringify(response));
                }
                socket.end();
            });
        });
        socket.on("error", err => {
            console.log("Socket error", err);
            socket.write(err.toString());
        });
    })
    .on("error", err => {
        console.log("Server error", err.message);
    })
    .listen(SERVER_PORT, SERVER_ADDRESS, (err) => {
        const addr = server.address();
        console.log("Listening: %s:%d (%s)", addr.address, addr.port, addr.family);
        // server.close(); // Shutdowns the server
    });

const commands = {
    ping: (payload, callback) => {
        setTimeout(() => {
            var response = "Pong: " + new Date();
            callback(null, response);
        }, 1000);
    },
    echo: (payload, callback) => {
        var data = get(payload, "data", "No data");
        callback(null, data);
    },
    setup: (payload, callback) => {
        var options = {cwd: __dirname};
        var cmd = "npm i";
        child_process.exec(cmd, options, (error, stdout, stderr) => {
            if (error) return callback(error);
            callback(null, stdout);
        });
    },
    shutdown: (data, callback) => {
        var server = data.server;
        server.close();
        callback();
    },
};