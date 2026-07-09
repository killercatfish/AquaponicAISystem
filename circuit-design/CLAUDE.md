# CLAUDE.md — circuit-design/ (Node 0 hardware work)

*Auto-loaded when working in this directory. Josh returns to this after a gap of
weeks/months — orient fully before acting.*

## Read in this order
1. `CIRCUIT_CONTEXT.md` — hardware state, constraints, what failed and why.
2. `BOARD1_LIGHT_CONTROLLER_REBUILD.md` — the finalized Board 1 deliverable (and the
   **format template** for every future board doc).
3. `FABLE_PROMPT.md` — the working brief: ground rules, deliverable format, priority list.
4. Firmware/control truth lives in the repo: `esp32/hlg_light_controller/hlg_light_controller.ino`,
   `esp32/LIGHT_CONTROLLER.md`, `src/hydroponics/sensors/light_controller.py`.

## State as of 2026-07-09
- **Board 1 (light controller rebuild): designed and finalized, NOT built.**
  Key design change: socketing the ESP32 forced the transistor circuit off rows 1–15
  (full header ties every row to an ESP32 pin; old layout would put ~10V on GPIO2).
  Details + rationale in the Board 1 doc.
- **Next physical action:** banner-test both ESP32 DevKits bare on the Mac
  (`screen /dev/cu.usbserial-XXXX 115200`, press EN, expect boot ROM text).
  Decides which module gets socketed. No bench needed.
- Boards 2–5 (relay split, consolidated sensor board, EC+DO wiring, analog TDS):
  **not yet designed.** Priority order is in FABLE_PROMPT.md / CIRCUIT_CONTEXT.md.

## Ground rules (non-negotiable — full text in FABLE_PROMPT.md)
- **Never state a GPIO pin, I2C address, device path, or IP from memory.** Verify in
  the repo, via brain_search, or ask Josh to run the check (`i2cdetect -y 1`, etc.).
  The I2C bus read EMPTY on last check — assume nothing is wired until confirmed.
- Unsure → write "⚠️ unverified — confirm X". Never bury a guess in a diagram.
- Socket every IC. Pump + heater must end up independently switchable.
- LLM never in the control/dosing path; deterministic Pi rules engine only.
- HLG AC side is 120V/lethal; only BLUE/WHITE dim wires are low-voltage. GFCI always.

## Known corrections (don't regress these)
- Serial protocol is **`SET:75`** / `GET` / `FADE:pct:secs` — *not* `SET_BRIGHTNESS:`.
  Verified 2026-07-08 in firmware + light_controller.py.
- Repo-root `CLAUDE_CONTEXT.md` is **stale (2026-03-27)** — it predates the May
  teardown (claims pH live at 0x63; bus was empty 5/14). Trust order:
  brain > CIRCUIT_CONTEXT.md > older docs.
- Configure the Pi serial port via `/dev/serial/by-id/` once known — `/dev/ttyUSB0`
  renumbers, and a stale regular file once blocked the device node.

## How Josh works
Short, direct, fragments fine. One thing at a time — give the **single next physical
action**, not a parallel list. Physical-first: he tests at the bench and reports back.
Deliverables = markdown matching the Board 1 doc's seven sections (layout grid →
placement → electrical paths → pre-power meter checklist → BOM → power-up → troubleshooting).
