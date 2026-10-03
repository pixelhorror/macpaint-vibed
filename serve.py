#!/usr/bin/env python3
"""Sirve MacPaint localmente.

Uso:
    python3 serve.py              # puerto 8000, abre el navegador
    python3 serve.py -p 9000      # otro puerto
    python3 serve.py --lan        # accesible desde otros dispositivos de la red (p. ej. tu móvil)
    python3 serve.py --no-open    # no abrir el navegador
"""
import argparse
import functools
import http.server
import os
import socket
import sys
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGE = "macpaint.html"


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(302)
            self.send_header("Location", "/" + PAGE)
            self.end_headers()
            return
        super().do_GET()

    def end_headers(self):
        # Sin caché: al recargar siempre ves la última versión del archivo
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write(f"  {self.address_string()}  {fmt % args}\n")


def lan_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return None


def main():
    ap = argparse.ArgumentParser(description="Servidor local para MacPaint")
    ap.add_argument("-p", "--port", type=int, default=8000)
    ap.add_argument("--lan", action="store_true", help="escuchar en 0.0.0.0 (red local)")
    ap.add_argument("--no-open", action="store_true", help="no abrir el navegador")
    args = ap.parse_args()

    if not os.path.exists(os.path.join(ROOT, PAGE)):
        sys.exit(f"No encuentro {PAGE} en {ROOT}")

    host = "0.0.0.0" if args.lan else "127.0.0.1"
    handler = functools.partial(Handler, directory=ROOT)
    try:
        httpd = http.server.ThreadingHTTPServer((host, args.port), handler)
    except OSError as e:
        sys.exit(f"No se pudo usar el puerto {args.port}: {e}. Prueba con -p 8080")

    url = f"http://localhost:{args.port}/{PAGE}"
    print(f"MacPaint servido en {url}")
    if args.lan and (ip := lan_ip()):
        print(f"En tu red local:   http://{ip}:{args.port}/{PAGE}")
        print("  (por HTTP en la red local no hay instalación ni modo offline: el navegador exige HTTPS)")
    print("Ctrl+C para detener\n")

    if not args.no_open:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
