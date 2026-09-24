"""
arduino.py
----------
IoT Module for Bhandarkars' Arts & Science College Smart Kiosk.
Handles PIR motion sensor communication via Arduino Serial or Simulated IoT State.

Supported Hardware:
- Arduino Uno / Nano / Mega with PIR Sensor connected to digital input
- Messages: 'PERSON_DETECTED' -> Action 'WELCOME'
           'NO_PERSON'        -> Action 'STANDBY'
"""

import sys
import time
import threading
from typing import Optional, Callable, List, Dict, Any

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    serial = None

# Default settings
DEFAULT_BAUD_RATE = 9600
SERIAL_PORT = "COM3"


class IoTStateManager:
    """Thread-safe state manager for PIR motion sensor events."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._current_state = "STANDBY"
        self._last_event_time = time.time()
        self._connected = False
        self._port_name: Optional[str] = None
        self._callbacks: List[Callable[[str], None]] = []

    def register_callback(self, callback: Callable[[str], None]):
        """Register a callback for state changes."""
        with self._lock:
            self._callbacks.append(callback)

    def trigger_event(self, message: str) -> str:
        """Processes PIR message ('PERSON_DETECTED' or 'NO_PERSON') and returns action."""
        action = "STANDBY"
        if message == "PERSON_DETECTED":
            action = "WELCOME"
        elif message == "NO_PERSON":
            action = "STANDBY"
        else:
            action = message

        with self._lock:
            self._current_state = action
            self._last_event_time = time.time()
            callbacks = list(self._callbacks)

        for cb in callbacks:
            try:
                cb(action)
            except Exception as e:
                print(f"[IoT] Callback error: {e}", flush=True)

        return action

    def get_status(self) -> Dict[str, Any]:
        """Returns the current state of the IoT PIR sensor."""
        with self._lock:
            return {
                "state": self._current_state,
                "connected": self._connected,
                "port": self._port_name,
                "last_event_time": self._last_event_time,
                "seconds_since_last_event": round(time.time() - self._last_event_time, 1)
            }

    def set_connected(self, connected: bool, port: Optional[str] = None):
        with self._lock:
            self._connected = connected
            self._port_name = port


# Global singleton instance
iot_manager = IoTStateManager()


def auto_detect_serial_port() -> Optional[str]:
    """Finds an available Arduino / USB Serial port across Windows, macOS, and Linux."""
    if serial is None:
        return None

    try:
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            # Common Arduino / USB serial identifiers
            port_lower = port.description.lower()
            hwid_lower = port.hwid.lower()
            if any(id_str in port_lower or id_str in hwid_lower for id_str in ["arduino", "usb", "ch340", "ftdi", "silicon labs", "tty"]):
                return port.device
        if ports:
            return ports[0].device
    except Exception as e:
        print(f"[IoT] Serial port scan error: {e}", flush=True)

    return None


def connect_arduino(port: Optional[str] = None, baud_rate: int = DEFAULT_BAUD_RATE):
    """Establishes connection to physical Arduino."""
    if serial is None:
        print("[IoT Notice] 'pyserial' library not installed. Running in simulation mode.", flush=True)
        iot_manager.set_connected(False, "Simulated")
        return None

    target_port = port or auto_detect_serial_port() or SERIAL_PORT

    try:
        arduino = serial.Serial(target_port, baud_rate, timeout=1)
        time.sleep(2)  # Wait for Arduino bootloader reset
        print(f"[IoT] Arduino connected successfully on {target_port}!", flush=True)
        iot_manager.set_connected(True, target_port)
        return arduino
    except Exception as e:
        print(f"[IoT] Arduino connection to {target_port} failed ({e}). Running in simulation mode.", flush=True)
        iot_manager.set_connected(False, f"Simulated ({target_port} offline)")
        return None


def read_arduino(arduino) -> Optional[str]:
    """Reads a line of text from the Arduino serial stream."""
    if not arduino:
        return None
    try:
        if arduino.in_waiting > 0:
            return arduino.readline().decode("utf-8", errors="ignore").strip()
    except Exception as e:
        print(f"[IoT] Error reading Arduino: {e}", flush=True)
    return None


def process_pir_message(message: str) -> Optional[str]:
    """Translates raw sensor message to Kiosk action."""
    return iot_manager.trigger_event(message)


def start_iot_background_listener(port: Optional[str] = None) -> threading.Thread:
    """Launches non-blocking background daemon thread to monitor Arduino events."""
    def _worker():
        arduino = connect_arduino(port)
        while True:
            if arduino:
                try:
                    msg = read_arduino(arduino)
                    if msg:
                        action = process_pir_message(msg)
                        print(f"[IoT Background] Sensor: {msg} -> Kiosk Action: {action}", flush=True)
                except Exception as e:
                    print(f"[IoT Background] Read loop error: {e}", flush=True)
                    time.sleep(2)
            time.sleep(0.1)

    thread = threading.Thread(target=_worker, daemon=True, name="IoT-Serial-Worker")
    thread.start()
    return thread


if __name__ == "__main__":
    print("--------------------------------")
    print(" Smart Campus Arduino Backend")
    print("--------------------------------")

    arduino = connect_arduino()

    if arduino:
        print("Waiting for PIR messages from physical Arduino...")
        while True:
            message = read_arduino(arduino)
            if message:
                print("Arduino Message:", message)
                action = process_pir_message(message)
                if action:
                    print("Backend Action:", action)
                print()
            time.sleep(0.1)
    else:
        print("Simulation Mode Active. You can test events programmatically:")
        print("Triggering PERSON_DETECTED -> Action:", iot_manager.trigger_event("PERSON_DETECTED"))
        print("Current Status:", iot_manager.get_status())
        time.sleep(1)
        print("Triggering NO_PERSON -> Action:", iot_manager.trigger_event("NO_PERSON"))
        print("Current Status:", iot_manager.get_status())