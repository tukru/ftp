#!/usr/bin/env python3

import http.server
import socketserver
import socket
import os
import html
import urllib.parse
import shutil

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHARE_DIR = os.path.join(BASE_DIR, "Shared_Files")

os.makedirs(SHARE_DIR, exist_ok=True)
os.chdir(SHARE_DIR)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


class Handler(http.server.SimpleHTTPRequestHandler):

    def list_directory(self, path):
        files = sorted(os.listdir(path))

        page = """
<html>
<head>
<title>Kali File Share</title>
<style>
body { background:#111; color:#eee; font-family:Arial; padding:20px; }
h1 { color:#4cff4c; }
a { color:#4cff4c; font-size:18px; text-decoration:none; }
.box { background:#222; padding:15px; border-radius:10px; margin-bottom:20px; }
.file { background:#222; padding:10px; border-radius:8px; margin:8px 0; }
input, button { font-size:18px; margin-top:10px; }
</style>
</head>
<body>

<h1>Kali Local File Share</h1>

<div class="box">
<h2>Upload MP4 / File</h2>
<form method="post" enctype="multipart/form-data">
<input type="file" name="file">
<br><br>
<button type="submit">Upload</button>
</form>
</div>

<h2>Files</h2>
"""

        for filename in files:
            safe = html.escape(filename)
            quoted = urllib.parse.quote(filename)
            size = os.path.getsize(filename) / (1024 * 1024)

            page += f"""
<div class="file">
<a href="{quoted}" download>{safe}</a>
<br>
<small>{size:.2f} MB</small>
</div>
"""

        page += "</body></html>"

        encoded = page.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
        return None

    def do_POST(self):
        content_type = self.headers.get("Content-Type", "")

        if "multipart/form-data" not in content_type:
            self.send_error(400, "Bad upload")
            return

        boundary = content_type.split("boundary=")[-1].encode()
        remaining = int(self.headers.get("Content-Length", 0))

        line = self.rfile.readline()
        remaining -= len(line)

        line = self.rfile.readline()
        remaining -= len(line)

        filename = "uploaded_file"

        if b"filename=" in line:
            filename = line.decode(errors="ignore").split("filename=")[1]
            filename = filename.strip().strip('"')
            filename = os.path.basename(filename)

        line = self.rfile.readline()
        remaining -= len(line)

        line = self.rfile.readline()
        remaining -= len(line)

        filepath = os.path.join(SHARE_DIR, filename)

        print("Uploading:", filename)

        with open(filepath, "wb") as f:
            preline = self.rfile.readline()
            remaining -= len(preline)

            while remaining > 0:
                line = self.rfile.readline()
                remaining -= len(line)

                if boundary in line:
                    f.write(preline.rstrip(b"\r\n"))
                    break

                f.write(preline)
                preline = line

        print("Saved:", filepath)

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()


ip = get_ip()

print("=" * 50)
print("KALI FILE SHARE RUNNING")
print("=" * 50)
print()
print(f"Open from phone/laptop:")
print(f"http://{ip}:{PORT}")
print()
print("Shared folder:")
print(SHARE_DIR)
print()
print("Stop with CTRL + C")
print()

with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), Handler) as httpd:
    httpd.serve_forever()