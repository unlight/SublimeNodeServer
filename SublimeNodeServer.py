import getpass
import queue
import os
import platform
import socket
import subprocess
import sys
import time
import threading

import sublime

SERVER_ADDRESS = "127.0.0.1"
SERVER_PORT = 7093
SERVER_PATH = os.path.join(
    sublime.packages_path(),
    os.path.dirname(os.path.realpath(__file__)),
    "SublimeNodeServer.js"
    # "index.js"
)

def plugin_loaded():
    # Called when the Sublime Text API is ready for use
    print("ready")
    client = NodeThreadingClient()
    client.start()

    # client = socket.socket()
    # client.connect((SERVER_ADDRESS, SERVER_PORT))

    # client.send(bytes(str("Hello from plugin"), 'UTF-8'))
    # client.close()

    # data = sock.recv(1024)
    # sock.close()

    # print(data)
    # SublimeNodeServer.thread = SublimeNodeServer(SERVER_ADDRESS, SERVER_PATH)
    # SublimeNodeServer.thread.start()

    # SublimeNodeServer.thread.client.send("Hello...")
    # SublimeNodeServer.thread.client.send("...world!")

def plugin_unloaded():
    # Called just before the plugin is unloaded.
    if SublimeNodeServer.thread:
        SublimeNodeServer.thread.terminate()

class NodeThreadingClient(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self, name = "NodeClientThread")
        self.connected = False

    def run(self):
        client = socket.socket()
        client.connect((SERVER_ADDRESS, SERVER_PORT))
        client.send(bytes(str("Hello from plugin"), 'UTF-8'))
        data = client.recv(16 * 1024)
        print('Received:', repr(data))
        client.close()

    def terminate(self):
        # Disconnects from the node server and terminates this thread.
        self.connected = False


class SublimeNodeServer(threading.Thread):
    # Manages the node server and printing its output.

    thread = None

    def __init__(self, server_address, server_path):
        threading.Thread.__init__(self, name="SublimeNodeServerThread")
        self.server_address = server_address
        self.server_path = server_path
        self.child = None
        self.client = SublimeNodeClient(self.server_address)

    def run(self):
        env = os.environ.copy()
        try:
            child = subprocess.Popen(
                ["node", self.server_path, self.server_address],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            self.child = child
        except OSError:
            raise Exception(
                "Couldn't find `node` in `{0}`.".format(env["PATH"])
            )

        self.client.start()

        while child.poll() is None:
            stdout = child.stdout.readline().decode("utf-8")
            sys.stdout.write(stdout)

        stdout, stderr = child.communicate()
        stdout = stdout.decode("utf-8")
        stderr = stderr.decode("utf-8")
        if stdout:
            sys.stdout.write(stdout)
        if stderr:
            message = "Node server encountered an error.\n{0}".format(
                "\n".join(["> " + line for line in stderr.split("\n")])
            )
            raise Exception(message)

    def terminate(self):
        """Sends SIGINT to the node child process."""
        if self.client:
            self.client.terminate()
            self.client = None
        if self.child.poll() is None:
            self.child.terminate()
            self.child = None

class SublimeNodeClient(threading.Thread):
    """Manages communication with the node server."""

    BRIDGE_THROTTLE = 0.01
    CONNECT_TIMEOUT = 30

    def __init__(self, server_address):
        threading.Thread.__init__(self, name="SublimeNodeClientThread")
        self.server_address = server_address
        self.connected = False
        self.queue = queue.Queue()

    def run(self):
        client = socket.socket()
        client.connect((SERVER_ADDRESS, SERVER_PORT))
        end_time = time.time() + SublimeNodeClient.CONNECT_TIMEOUT
        while not self.connected:
            remaining_time = end_time - time.time()
            if remaining_time < 0:
                raise Exception(
                    "Unable to connect to `{0}`".format(self.server_address)
                )
            try:
                client.connect(self.server_address)
                self.connected = True
            except (ConnectionRefusedError, FileNotFoundError):
                pass

        while self.connected:
            while not self.queue.empty():
                (message, callback) = self.queue.get()
                encoded = sublime.encode_value(message) + "\n"
                client.send(bytes(encoded, "utf-8"))
                if callback:
                    sublime.set_timeout(callback, 0)
            time.sleep(SublimeNodeClient.BRIDGE_THROTTLE)

        client.close()

    def send(self, message, callback=None):
        """Sends a message to the node server."""
        self.queue.put((message, callback))

    def terminate(self):
        """Disconnects from the node server and terminates this thread."""
        self.connected = False
