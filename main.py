#!/usr/bin/env python3
"""Single root entry point for the Smart Campus Help Desk project."""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "app"
DB_PATH = BACKEND_DIR / "campus.db"
FRONTEND_DIR = BACKEND_DIR

for path in [str(ROOT_DIR), str(BACKEND_DIR)]:
    if path not in sys.path:
        sys.path.insert(0, path)


def ensure_database() -> None:
    """Create and seed the SQLite campus database if it does not exist."""
    if not DB_PATH.exists():
        print("[Database] campus.db not found. Initializing database...", flush=True)
        try:
            import databasse

            databasse.create_database()
            databasse.insert_campus_data()
            print("[Database] Database initialized and seeded successfully!", flush=True)
        except Exception as exc:  # pragma: no cover - startup safety check
            print(f"[Database Error] Could not initialize database: {exc}", flush=True)
            raise
    else:
        print(f"[Database] SQLite campus database verified at: {DB_PATH}", flush=True)


def load_backend_app():
    """Load the Flask app from the canonical backend module."""
    backend_app_path = BACKEND_DIR / "app.py"
    spec = importlib.util.spec_from_file_location("smart_campus_backend", str(backend_app_path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load backend app from {backend_app_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["smart_campus_backend"] = module
    spec.loader.exec_module(module)
    return module.app


def print_banner(host: str, port: int) -> None:
    """Display a polished startup banner."""
    banner = f"""
======================================================================
  BHANDARKARS' ARTS & SCIENCE COLLEGE · SMART HELP DESK & NAVIGATION
======================================================================
  * Service:   Flask REST API + Web Kiosk
  * Frontend:  {FRONTEND_DIR.name}
  * Backend:   {BACKEND_DIR.name}
  * AI & Nav:  Dijkstra routing + NLP query engine
  * IoT:       Arduino PIR monitor (simulation if unavailable)
----------------------------------------------------------------------
  * Web Kiosk: http://{host}:{port}/
  * API Base:   http://{host}:{port}/api
  * IoT Status: http://{host}:{port}/api/iot/status
======================================================================
"""
    print(banner, flush=True)


def maybe_open_browser(host: str, port: int, no_browser: bool) -> None:
    """Open the default browser after startup unless disabled."""
    if no_browser or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        return

    def _open() -> None:
        time.sleep(1.2)
        url = f"http://{host}:{port}/"
        try:
            webbrowser.open(url)
        except Exception:
            pass

    threading.Thread(target=_open, daemon=True).start()


def start_iot_listener(serial_port: str | None = None) -> None:
    """Start the Arduino/PIR listener if available without crashing the app."""
    try:
        from arduino import start_iot_background_listener

        start_iot_background_listener(port=serial_port)
        print("[IoT] Background PIR motion sensor worker active.", flush=True)
    except Exception as exc:
        print(f"[IoT Notice] Serial monitor handshake skipped: {exc}", flush=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Start the Smart Campus Voice Help Desk & Navigation Kiosk"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host address to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default: 5000)")
    parser.add_argument("--debug", action="store_true", help="Run Flask in debug mode")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open the browser")
    parser.add_argument("--serial-port", default=None, help="Specific Arduino serial port (e.g. COM3 or /dev/tty.usbmodem...)")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    ensure_database()
    start_iot_listener(args.serial_port)
    print_banner(args.host, args.port)
    maybe_open_browser(args.host, args.port, args.no_browser)

    app = load_backend_app()
    app.run(host=args.host, port=args.port, debug=args.debug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
