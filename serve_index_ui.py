"""
Python UI สำหรับเปิด/ปิด HTTP server ที่รัน index.html ในโฟลเดอร์เดียวกัน
- Start: เปิดเว็บเซิร์ฟเวอร์และเปิดเบราว์เซอร์
- Stop: ปิดทุกโปรเซสที่เปิด localhost:* (ทุกพอร์ต)
"""
import os
import sys
import threading
import subprocess
import signal
import socket
import tkinter as tk
from tkinter import messagebox
import webbrowser
import http.server
import socketserver

PORT_DEFAULT = 8765

class ServerThread(threading.Thread):
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.httpd = None
        self.daemon = True

    def run(self):
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", self.port), handler) as httpd:
            self.httpd = httpd
            url = f"http://localhost:{self.port}/index.html"
            try:
                webbrowser.open(url)
            except Exception:
                pass
            try:
                httpd.serve_forever()
            except Exception:
                pass

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()


def kill_localhost_ports():
    """Kill all processes listening on localhost:* (Windows only)"""
    try:
        # netstat -ano | findstr LISTENING
        output = subprocess.check_output(
            'netstat -ano | findstr LISTENING', shell=True, encoding='utf-8', errors='ignore')
        pids = set()
        for line in output.splitlines():
            if '127.0.0.1:' in line or '0.0.0.0:' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids.add(int(pid))
        # Kill all found PIDs
        for pid in pids:
            try:
                if pid != os.getpid():
                    subprocess.run(f'taskkill /PID {pid} /F', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        return True
    except Exception as e:
        return False

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Localhost Server Controller")
        self.server_thread = None
        self.port = tk.IntVar(value=PORT_DEFAULT)
        self.status = tk.StringVar(value="Stopped")

        tk.Label(root, text="Port:").grid(row=0, column=0, padx=8, pady=8)
        tk.Entry(root, textvariable=self.port, width=8).grid(row=0, column=1, padx=8, pady=8)
        tk.Button(root, text="Start", command=self.start_server, width=10).grid(row=0, column=2, padx=8, pady=8)
        tk.Button(root, text="Stop ALL localhost", command=self.stop_all, width=18).grid(row=1, column=0, columnspan=3, padx=8, pady=8)
        tk.Label(root, textvariable=self.status, fg="green").grid(row=2, column=0, columnspan=3, pady=8)

    def start_server(self):
        if self.server_thread and self.server_thread.is_alive():
            messagebox.showinfo("Info", "Server already running!")
            return
        port = self.port.get()
        self.server_thread = ServerThread(port)
        self.server_thread.start()
        self.status.set(f"Running on localhost:{port}")

    def stop_all(self):
        killed = kill_localhost_ports()
        self.status.set("Stopped")
        if killed:
            messagebox.showinfo("Stopped", "Killed all processes on localhost:*")
        else:
            messagebox.showerror("Error", "Failed to kill processes.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
