"""
HLG-320H-48B PWM light controller via ESP32 over USB serial.

Firmware lives at esp32/hlg_light_controller/. Brightness is human 0-100%.
The firmware handles the inverted PWM logic internally.

Serial protocol (115200 baud):
    SET:75\\n       -> OK:BRIGHTNESS:75
    GET\\n          -> BRIGHTNESS:75
    FADE:100:30\\n  -> OK:FADING_TO:100:OVER:30s

Connection states:
    "connected"     — serial port open, controller responsive
    "disconnected"  — port couldn't be opened (no hardware, wrong path, etc.)
    "mock"          — pyserial isn't installed at all (dev environment)

Read/write methods return None or False when not connected so callers can
surface the truth instead of pretending success.
"""

import logging
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import serial
except ImportError:
    logger.warning("pyserial not installed, using mock light controller")
    serial = None


class LightController:
    """Serial interface to the ESP32 PWM dimmer driving the HLG-320H-48B."""

    def __init__(self, port: str = '/dev/ttyUSB0', baud: int = 115200, port_fallback: Optional[str] = None):
        self.port = port
        self.port_fallback = port_fallback
        self.baud = baud
        self.ser = None
        self._lock = threading.Lock()
        self._last_known_brightness: Optional[int] = None
        # State: "connected" | "disconnected" | "mock"
        self.state = "mock" if serial is None else "disconnected"

    @property
    def is_connected(self) -> bool:
        return self.state == "connected"

    def _try_open(self, port: str) -> bool:
        try:
            s = serial.Serial()
            s.port = port
            s.baudrate = self.baud
            s.timeout = 0.3
            s.dsrdtr = False
            s.rtscts = False
            s.open()
            # Park DTR/RTS low — opening pulses DTR which resets the ESP32, but
            # leaving RTS high holds EN low (chip stuck in reset).
            s.dtr = False
            s.rts = False
            time.sleep(0.5)
            s.reset_input_buffer()

            banner = s.read(512).decode('utf-8', errors='replace').strip()
            if banner:
                logger.info(f"ESP32 light controller @ {port}: {banner.splitlines()[0]}")

            self.ser = s
            self._last_known_brightness = 100
            self.state = "connected"
            logger.info(f"Light controller connected on {port}")
            return True
        except Exception as e:
            logger.warning(f"Could not open light controller on {port}: {e}")
            return False

    def initialize(self):
        """Open serial port, trying fallback if primary path is missing."""
        if serial is None:
            logger.warning("Light controller in MOCK MODE (pyserial unavailable)")
            return

        if self._try_open(self.port):
            return
        if self.port_fallback and self.port_fallback != self.port:
            logger.info(f"Trying fallback port {self.port_fallback}")
            if self._try_open(self.port_fallback):
                return

        logger.error(
            f"Light controller could not be opened on {self.port}"
            + (f" or {self.port_fallback}" if self.port_fallback else "")
        )
        self.state = "disconnected"

    def reconnect(self) -> bool:
        """Close any open port and try to open again. Returns True if connected."""
        with self._lock:
            if self.ser is not None:
                try:
                    self.ser.close()
                except Exception:
                    pass
                self.ser = None
            self.state = "mock" if serial is None else "disconnected"
            self.initialize()
            return self.is_connected

    def _send(self, command: str, read_bytes: int = 256) -> str:
        """Send a command and return the response. Caller must hold the lock."""
        self.ser.write((command + '\n').encode())
        self.ser.flush()
        time.sleep(0.15)
        return self.ser.read(read_bytes).decode('utf-8', errors='replace').strip()

    def _mark_disconnected(self, e: Exception):
        logger.error(f"Light controller serial error, marking disconnected: {e}")
        self.state = "disconnected"
        if self.ser is not None:
            try:
                self.ser.close()
            except Exception:
                pass
            self.ser = None

    def set_brightness(self, pct: int) -> bool:
        """Set brightness 0-100%. Returns True only if a real serial write succeeded."""
        pct = max(0, min(100, int(pct)))
        if not self.is_connected:
            logger.warning(f"set_brightness({pct}) ignored — controller {self.state}")
            return False

        with self._lock:
            try:
                resp = self._send(f"SET:{pct}")
                if resp.startswith("OK:BRIGHTNESS:"):
                    self._last_known_brightness = pct
                    return True
                logger.warning(f"Unexpected SET response: {resp!r}")
                return False
            except Exception as e:
                self._mark_disconnected(e)
                return False

    def get_brightness(self) -> Optional[int]:
        """Read current brightness. Returns None if not connected."""
        if not self.is_connected:
            return None

        with self._lock:
            try:
                resp = self._send("GET")
                # Last matching line — fade progress can sit ahead in the buffer.
                for line in reversed(resp.splitlines()):
                    if line.startswith("BRIGHTNESS:"):
                        value = int(line.split(":", 1)[1])
                        self._last_known_brightness = value
                        return value
                logger.warning(f"Unexpected GET response: {resp!r}")
                return self._last_known_brightness
            except Exception as e:
                self._mark_disconnected(e)
                return None

    def fade_to(self, pct: int, seconds: int) -> bool:
        """Fade to brightness over duration. Returns True only if firmware acked."""
        pct = max(0, min(100, int(pct)))
        seconds = max(0, int(seconds))
        if not self.is_connected:
            logger.warning(f"fade_to({pct},{seconds}) ignored — controller {self.state}")
            return False

        with self._lock:
            try:
                resp = self._send(f"FADE:{pct}:{seconds}")
                if resp.startswith("OK:FADING_TO:"):
                    self._last_known_brightness = pct
                    return True
                logger.warning(f"Unexpected FADE response: {resp!r}")
                return False
            except Exception as e:
                self._mark_disconnected(e)
                return False

    def cleanup(self):
        if self.ser is not None:
            try:
                self.ser.close()
            except Exception:
                pass
        logger.info("Light controller closed")


# Global instance
light_controller = LightController()
