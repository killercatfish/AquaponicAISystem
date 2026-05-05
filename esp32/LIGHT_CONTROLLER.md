# ESP32 Light Controller — HLG-320H-48B PWM Dimmer

**Hardware:** ESP32 DevKit V1 (30-pin, micro USB)  
**Driver:** Mean Well HLG-320H-48B (Type B — PWM dimming)  
**Board:** EPLZON perfboard (A-E columns, 15 rows per side, rows connected horizontally)  
**Firmware:** `light_controller.ino`  
**Connected to:** Raspberry Pi aquapi via USB serial (15ft micro USB cable)

---

## Perfboard layout

Board is viewed from the **back/bottom** (solder side). Rows are horizontally connected — everything in the same row is electrically tied together.

```
     1    2    3    4    5    6    7    8    9   10   11   12
A    .    .    .    .    .    .    .    .    .    .    .    .
B    .   GND   .    .    .    .    .   GPIO18 .    .    .    .
C    .    .    R    .    .    .    .    .    R    .    .    .
D    .    E    B    C    .    .    .    .    .    .    .    .
E    .    W    .   BL    .    .    .    .    .    .    .    .
```

### Component placement

| Component | Location | Notes |
|---|---|---|
| Resistor (1kΩ) | C3 and C9 | Vertical, long legs bent to span rows |
| 2N2222 Emitter | D2 | Flat face of transistor facing you |
| 2N2222 Base | D3 | Middle leg |
| 2N2222 Collector | D4 | Right leg |
| HLG WHITE wire (Dim−) | E2 | Soldered alongside Emitter leg |
| HLG BLUE wire (Dim+) | E4 | Soldered alongside Collector leg |
| ESP32 GPIO18 | B9 | Pin 8 on left side of 30-pin DevKit |
| ESP32 GND | B2 | Pin 2 on left side of 30-pin DevKit |

### How the row connections do the work

No jumper bridges needed — rows handle everything:

- **Row 2:** B2(GND) + D2(Emitter) + E2(WHITE) — all tied together
- **Row 3:** C3(resistor bottom) + D3(Base) — resistor feeds Base automatically
- **Row 4:** D4(Collector) + E4(BLUE) — Collector tied to Dim+
- **Row 9:** B9(GPIO18) + C9(resistor top) — GPIO18 feeds resistor automatically

---

## Circuit logic

```
GPIO18 → 1kΩ resistor → Transistor Base
GND → Transistor Emitter + HLG WHITE (Dim−)
HLG BLUE (Dim+) → Transistor Collector
```

**Inverted PWM logic** (HLG-320H-48B Type B behavior):

| PWM duty | Transistor | Light |
|---|---|---|
| 0% (duty 0) | OFF — Dim+ floating | Full brightness |
| 50% (duty 128) | Half conducting | ~50% brightness |
| 100% (duty 255) | ON — Dim+ pulled to GND | Minimum (~10%) |

The transistor shorts Dim+ to Dim− when ON, which tells the driver to dim.

---

## Serial protocol

ESP32 listens on USB serial at **115200 baud**. Pi sends commands as plain text with `\n` terminator.

| Command | Example | Response |
|---|---|---|
| Set brightness | `SET:75\n` | `OK:BRIGHTNESS:75` |
| Get brightness | `GET\n` | `BRIGHTNESS:75` |
| Fade to level | `FADE:100:10\n` | `OK:FADING_TO:100:OVER:10s` |
| Run test cycle | `TEST\n` | cycles through levels, prints status |

Brightness is **0–100%** (human-readable). Firmware handles the PWM inversion internally.

---

## Firmware modes

Set at top of `light_controller.ino`:

```cpp
#define TEST_MODE true   // standalone test — cycles brightness on boot
#define TEST_MODE false  // Pi serial control mode
```

---

## How to flash

1. Connect ESP32 to Mac via micro USB
2. Open `light_controller.ino` in Arduino IDE or via `arduino-cli`
3. Board: `ESP32 Dev Module`
4. Set `TEST_MODE true` for first test
5. Upload
6. Watch light cycle — if it dims and brightens, hardware is good
7. Set `TEST_MODE false`, re-upload, plug into Pi

---

## Pi serial commands (Python)

```python
import serial

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

def set_brightness(pct):
    ser.write(f"SET:{pct}\n".encode())
    return ser.readline().decode().strip()

def get_brightness():
    ser.write(b"GET\n")
    return ser.readline().decode().strip()

def fade_to(pct, seconds):
    ser.write(f"FADE:{pct}:{seconds}\n".encode())
    return ser.readline().decode().strip()
```

---

## Physical location

Board mounts **up high inside the grow tent**, near the HLG driver. 15ft micro USB cable runs down to the Pi at reservoir level. HLG BLUE and WHITE dimming wires are short — soldered directly to board, no connectors.

---

## Open items

- [ ] Confirm `/dev/ttyUSB0` is correct port on aquapi (may be `ttyUSB0` or `ttyUSB1`)
- [ ] Write Pi-side integration script to call SET/GET on schedule
- [ ] Implement sunrise/sunset schedule (6am ramp up, 8pm ramp down)
- [ ] Add light level to SQLite sensor readings
