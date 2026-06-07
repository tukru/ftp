#!/usr/bin/env python3

import http.server
import socketserver
import socket
import os
import cgi
import html
import urllib.parse

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


class FileShareHandler(http.server.SimpleHTTPRequestHandler):

    def list_directory(self, path):

        files = sorted(os.listdir(path))

        page = """
<html>
<head>
<title>Kali File Share</title>

<style>
body {
    background: #111;
    color: #eee;
    font-family: Arial;
    padding: 20px;
}

h1 {
    color: #4cff4c;
}

a {
    color: #4cff4c;
    text-decoration: none;
    font-size: 18px;
}

.file {
    background: #222;
    padding: 10px;
    border-radius: 8px;
    margin: 10px 0;
}

.box {
    background: #222;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
}
</style>

</head>

<body>

<h1>Kali Local File Share</h1>

<div class="box">

<h2>Upload File</h2>

<form enctype="multipart/form-data" method="post">

<input name="file" type="file">

<br><br>

<button type="submit">
Upload
</button>

</form>

</div>

<h2>Files</h2>
"""

        for filename in files:

            safe_name = html.escape(filename)

            quoted_name = urllib.parse.quote(filename)

            page += f'''
<div class="file">
<a href="{quoted_name}" download>
{safe_name}
</a>
</div>
'''

        page += """
</body>
</html>
"""

        encoded = page.encode("utf-8")

        self.send_response(200)

        self.send_header(
            "Content-type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(encoded))
        )

        self.end_headers()

        self.wfile.write(encoded)

        return None


    def do_POST(self):

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers.get("Content-Type"),
            }
        )

        if "file" in form:

            file_item = form["file"]

            if file_item.filename:

                filename = os.path.basename(
                    file_item.filename
                )

                filepath = os.path.join(
                    SHARE_DIR,
                    filename
                )

                with open(filepath, "wb") as f:
                    f.write(file_item.file.read())

                print("Uploaded:", filename)

        self.send_response(303)

        self.send_header("Location", "/")

        self.end_headers()


ip = get_ip()

print("=" * 50)
print("KALI FILE SHARE RUNNING")
print("=" * 50)

print()
print("Open this address on another device:")
print(f"http://{ip}:{PORT}")
print()

print("Shared folder:")
print(SHARE_DIR)

print()
print("Press CTRL + C to stop")
print()

with socketserver.TCPServer(
    ("0.0.0.0", PORT),
    FileShareHandler
) as httpd:

    httpd.serve_forever()