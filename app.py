"""Run MarketLens with: python app.py"""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import webbrowser

from marketlens.service import Service

ROOT = Path(__file__).resolve().parent


def make_handler(service):
    class Handler(BaseHTTPRequestHandler):
        def respond(self, status, data, content_type="application/json; charset=utf-8"):
            body = json.dumps(data, allow_nan=False).encode() if isinstance(data, dict) else data
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/api/state":
                try:
                    mode = parse_qs(urlparse(self.path).query).get("mode", ["current"])[0]
                    return self.respond(200, service.snapshot(mode) if getattr(service, "is_mvp", False) else service.snapshot())
                except ValueError as error:
                    return self.respond(400, {"error": str(error)})
            files = {"/": ("index.html", "text/html"), "/style.css": ("style.css", "text/css"),
                     "/app.js": ("app.js", "text/javascript"),
                     "/mvp.js": ("mvp.js", "text/javascript"),
                     "/journey.js": ("journey.js", "text/javascript")}
            if path not in files:
                return self.respond(404, {"error": "Not found."})
            filename, mime = files[path]
            self.respond(200, (ROOT / "web" / filename).read_bytes(), mime + "; charset=utf-8")

        def do_POST(self):
            # The local demo permits writes only from its own browser origin.
            origin = self.headers.get("Origin")
            if origin and origin != f"http://{self.headers.get('Host')}":
                return self.respond(403, {"error": "Cross-origin requests are not allowed."})
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                return self.respond(415, {"error": "Expected application/json."})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 4096:
                    raise ValueError("Invalid request size.")
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict):
                    raise ValueError("Expected a JSON object.")
                path = urlparse(self.path).path
                options = {"mode": data.get("mode", "current")} if getattr(service, "is_mvp", False) else {}
                if path == "/api/portfolio":
                    service.create_portfolio(data.get("profile"), data.get("balance"), **options)
                elif path == "/api/advance":
                    service.advance(**options)
                elif path == "/api/reset":
                    service.reset(**options)
                elif path == "/api/refresh" and getattr(service, "is_mvp", False):
                    service.request_refresh()
                else:
                    return self.respond(404, {"error": "Not found."})
                self.respond(200, service.snapshot(**options))
            except (ValueError, TypeError, UnicodeError) as error:
                self.respond(400, {"error": str(error)})

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--database", type=Path, default=ROOT / ".runtime" / "marketlens.sqlite3")
    args = parser.parse_args()
    try:
        from marketlens.mvp import MVPService
        service = MVPService(ROOT / "data" / "training_prices.csv", args.database)
        server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(service))
    except (ValueError, OSError) as error:
        parser.exit(1, f"MarketLens could not start: {error}\n")
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"MarketLens is running at {url}. Press Ctrl+C to stop.", flush=True)
    service.start()
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        service.stop()


if __name__ == "__main__":
    main()
