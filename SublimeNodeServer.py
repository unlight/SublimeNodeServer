import sublime
import sublime_plugin
import os
import subprocess
import threading
import socket
import json

package_path = os.path.dirname(os.path.realpath(__file__));
server_path = "node-server.js"
server_address = "127.0.0.1"
server_port = 7093

plugin_info = {}

def plugin_file_path():
    s = len(sublime.packages_path())
    return __file__[s:]

def plugin_loaded():
    print("plugin_loaded", plugin_file_path())
    server_thread = threading.Thread(target=server_process, args=())
    server_thread.start()

def server_process():
    cmd = ["node", server_path, server_address, str(server_port)]
    if os.name == "nt":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.SW_HIDE | subprocess.STARTF_USESHOWWINDOW
        proc = subprocess.Popen(cmd, cwd=package_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, startupinfo=si)
    else:
        proc = subprocess.Popen(cmd, cwd=package_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    outs, errs = proc.communicate()
    print(outs)
    plugin_info["server_proc_pid"] = proc.pid

def plugin_unloaded():
    print("plugin_unloaded", plugin_file_path())
    send_command("shutdown")
    
def send_command(command, data = None):
    client = socket.socket()
    client.connect((server_address, server_port))
    message = json.dumps({"command": command, "data": data})
    print('message', message)
    client.send(message.encode('utf-8'))
    recv = client.recv(16 * 1024).decode('utf-8')
    print('recv', recv)
    client.close()

class NodeServerEventListener(sublime_plugin.EventListener):
    
    def on_close(self, view):
        window = sublime.active_window()
        if window is None or not window.views():
            send_command("shutdown")

# view.run_command("test_node_server_ping")
class TestNodeServerPingCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        send_command("ping")

# view.run_command("test_node_server_echo")
class TestNodeServerEchoCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        send_command("echo", "Hello from sublime")

class TestNodeServerTextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        pass


