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
                var data = JSON.parse(chunk.toString());    
            } catch (err) {
                return socket.emit("error", err);
            }
            data.socket = socket;
            data.server = server;
            var cmd = get(data, "command");
            console.log("Command: " + cmd);
            var func = get(commands, cmd, (data, callback) => callback());
            func(data, (err, response) => {
                if (err) return socket.emit("error", err);
                if (response) {
                    socket.write(response);
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
        console.log("Listening %s:%d (%s)", addr.address, addr.port, addr.family);
        // server.close(); // Shutdowns the server
    });

const commands = {
    ping: (data, callback) => {
        setTimeout(() => {
            var response = "Pong: " + new Date();
            callback(null, response);
        }, 1000);
    },
    echo: (payload, callback) => {
        var data = get("data", payload, "No data");
        callback(null, JSON.stringify(data));
    },
    setup: (data, callback) => {
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