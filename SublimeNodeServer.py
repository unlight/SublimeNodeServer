import sublime
import sublime_plugin
import os
import subprocess
import threading

# server_path = os.path.join(sublime.packages_path(), os.path.printname(os.path.realpath(__file__)), "node-server.js")
package_path = os.path.dirname(os.path.realpath(__file__));
server_path = "node-server.js"
server_address = "127.0.0.1"
server_port = "7093"

server_thread = None
server_proc = None

def server_process():
    global server_proc, server_thread
    if os.name == "nt":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.SW_HIDE | subprocess.STARTF_USESHOWWINDOW
        server_proc = subprocess.Popen(["node", server_path, server_address, server_port], cwd=package_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, startupinfo=si)
    else:
        server_proc = subprocess.Popen(["node", server_path, server_address, server_port], cwd=package_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    print('server_proc')
    print(server_proc)
    outs, errs = server_proc.communicate()
    print(outs)
    print(errs)
    print('server_process server_proc.pid', server_proc.pid)

def plugin_loaded():
    global server_proc, server_thread
    print("plugin_loaded")
    server_thread = threading.Thread(target=server_process, args=())
    server_thread.start()
    print('After server_thread')
    print('server_proc', server_proc)
    print('server_proc.pid', server_proc.pid)

def plugin_unloaded():
    global server_proc, server_thread
    print("plugin_unloaded")
    if (server_proc):
        server_proc.kill()
        print('server_proc')
        print(server_proc)
    
class TestNodeServerTextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global server_proc, server_thread
        print(server_proc)
        print('server_proc.pid', server_proc.pid)
        print(server_thread)
        server_proc.kill()