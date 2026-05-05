"""
HLG-320H-48B PWM light controller via ESP32 over USB serial.

Firmware lives at esp32/hlg_light_controller/. Brightness is human 0-100%.
The firmware handles the inverted PWM logic internally.

Serial protocol (115200 baud):
    SET:75\\n       -> OK:BRIGHTNESS:75
    GET\\n          -> BRIGHTNESS:75
    FADE:100:30\\n  -> OK:FADING_TO:100:OVER:30s
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

    def __init__(self, port: str = '/dev/ttyUSB0', baud: int = 115200):
        self.port = port
        self.baud = baud
        self.ser = None
        self.mock_mode = serial is None
        self._lock = threading.Lock()
        self._last_known_brightness: Optional[int] = None

    def initialize(self):
        """Open serial port and read the firmware boot banner."""
        if self.mock_mode:
            logger.warning("Light controller in MOCK MODE (pyserial unavailable)")
            self._last_known_brightness = 100
            return

        try:
            s = serial.Serial()
            s.port = self.port
            s.baudrate = self.baud
            s.timeout = 0.3
            s.dsrdtr = False
            s.rtscts = False
            s.open()
            # Opening pulses DTR which resets the ESP32. Park DTR/RTS low so the
            # chip stays out of reset; otherwise the firmware never starts.
            s.dtr = False
            s.rts = False
            time.sleep(0.5)
            s.reset_input_buffer()

            # Drain boot banner so the first user command isn't shadowed by it.
            banner = s.read(512).decode('utf-8', errors='replace').strip()
            if banner:
                logger.info(f"ESP32 light controller: {banner.splitlines()[0]}")

            self.ser = s
            # Firmware sets brightness to 100 on boot.
            self._last_known_brightness = 100
            logger.info(f"Light controller initialized on {self.port}")
        except Exception as e:
            logger.error(f"Could not open light controller on {self.port}: {e}")
            self.mock_mode = True
            self._last_known_brightness = 100

    def _send(self, command: str, read_bytes: int = 256) -> str:
        """Send a command and return the response. Caller must hold the lock."""
        self.ser.write((command + '\n').encode())
        self.ser.flush()
        time.sleep(0.15)
        return self.ser.read(read_bytes).decode('utf-8', errors='replace').strip()

    def set_brightness(self, pct: int) -> bool:
        """Set brightness 0-100%. Returns True on success."""
        pct = max(0, min(100, int(pct)))
        if self.mock_mode:
            self._last_known_brightness = pct
            logger.info(f"Mock light: SET:{pct}")
            return True

        with self._lock:
            try:
                resp = self._send(f"SET:{pct}")
                if resp.startswith("OK:BRIGHTNESS:"):
                    self._last_known_brightness = pct
                    return True
                logger.warning(f"Unexpected SET response: {resp!r}")
                return False
            except Exception as e:
                logger.error(f"Error setting brightness: {e}")
                return False

    def get_brightness(self) -> Optional[int]:
        """Read current brightness from the firmware."""
        if self.mock_mode:
            return self._last_known_brightness

        with self._lock:
            try:
                resp = self._send("GET")
                # Last line because a stale fade-progress line could be ahead of it.
                for line in reversed(resp.splitlines()):
                    if line.startswith("BRIGHTNESS:"):
                        value = int(line.split(":", 1)[1])
                        self._last_known_brightness = value
                        return value
                logger.warning(f"Unexpected GET response: {resp!r}")
                return self._last_known_brightness
            except Exception as e:
                logger.error(f"Error reading brightness: {e}")
                return self._last_known_brightness

    def fade_to(self, pct: int, seconds: int) -> bool:
        """Fade to brightness over the given duration. Non-blocking on the firmware side."""
        pct = max(0, min(100, int(pct)))
        seconds = max(0, int(seconds))
        if self.mock_mode:
            self._last_known_brightness = pct
            logger.info(f"Mock light: FADE:{pct}:{seconds}")
            return True

        with self._lock:
            try:
                resp = self._send(f"FADE:{pct}:{seconds}")
                if resp.startswith("OK:FADING_TO:"):
                    # Optimistic — firmware confirms the fade started, will end at pct.
                    self._last_known_brightness = pct
                    return True
                logger.warning(f"Unexpected FADE response: {resp!r}")
                return False
            except Exception as e:
                logger.error(f"Error starting fade: {e}")
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
