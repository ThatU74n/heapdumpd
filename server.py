from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import subprocess

OUTPUT_DIR = "/home/ubuntu/heapdump/dump"


def get_pm2_pid():
    # Capture pm2 list as JSON
    try:
        pm2_output = subprocess.check_output(
            ["pm2", "jlist"], text=True
        )
    except Exception as e:
        raise RuntimeError(f"Failed to run pm2 jlist: {e}")

    # Use jq to extract PID
    try:
        pid = subprocess.check_output(
            ["jq", "-r", ".[] | select(.name==\"api\") | .pid"],
            input=pm2_output,
            text=True
        ).strip()
    except Exception as e:
        raise RuntimeError(f"Failed to extract PID: {e}")

    # ---- SANITIZE PID ----
    if not pid.isdigit():
        raise ValueError(f"Invalid PID: {pid}")

    pid_int = int(pid)
    if pid_int <= 0 or pid_int > 999999:
        raise ValueError(f"PID out of expected range: {pid_int}")

    return pid_int


def trigger_heap_dump(pid: int):
    # Use argument list to avoid shell injection
    now = datetime.now()
    filename = f"{OUTPUT_DIR}/{now.strftime('heapdump-%Y%m%d-%H%M.hprof')}"
    cmd = ["jcmd", str(pid), "GC.heap_dump", filename]

    subprocess.run(cmd, check=True)


class Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            pid = get_pm2_pid()
            trigger_heap_dump(pid)
            self.send_response(201)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
            return

        self.end_headers()


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 2367), Handler)
    server.serve_forever()
