# CIRCUIT_CONTEXT.md — Node 0 Hardware & Circuit State

*Context file for circuit-design work. Written for CC Fable to read first.*
*Last verified against JARVIS brain: 2026-07-07. Source captures dated Mar–May 2026.*

> **⚠️ Verification rule.** Anything with a ⚠️ is not eyes-on-confirmed and must be
> checked on the Pi / at the bench / in the repo before a design depends on it.
> Do not treat an IP, GPIO pin, I2C address, device path, or repo path in this file
> as ground truth without re-confirming. Brain > this doc > older project docs.

---

## Machines & network (confirmed 2026-05-14)

| Host | What | Tailscale IP | Notes |
|------|------|--------------|-------|
| aquapi | Raspberry Pi 5 Model B Rev 1.1, 8GB | 100.117.109.76 | Always-on hub. Hostname is `aquaponics`; SSH alias `aquapi` differs. 3 I2C buses available. |
| macdev | MacBook Air M2, 8GB, macOS 26.0.1 | 100.97.91.42 | Where you work / run Claude Code. Hostname `joshs-macbook-air`. |
| KCFGAMER | Windows 11, RTX 4070 Ti 12GB | 100.75.168.92 | Ollama (qwen2.5:14b, llava). Advisory tier only. |

---

## Control architecture (the shape it has to fit)

- **Pi = brain.** Deterministic rules engine (YAML config). This is the ONLY thing in the control/dosing decision path.
- **Ollama = advisory only.** Trend analysis, plain-English explanations. Never in the control loop.
- **ESP32 = light PWM controller.** Talks to Pi over USB serial. Protocol is dead simple: `SET:75` (verified 2026-07-08 in `hlg_light_controller.ino` + `light_controller.py` — older docs saying `SET_BRIGHTNESS:` are wrong).
- **Relay = DLI IoT Relay II** on a single GPIO input → this is the ganging problem (see below).

**Hard constraints — no design may violate these:**
1. LLM never in the dosing/control decision path. Rules engine stays deterministic.
2. Dead-man's switch: halt all dosing if any sensor goes stale > 5 min.
3. Socket every IC. No direct-soldered ESP32 ever again — joints must be inspectable/replaceable.
4. Pump and heater must be independently switchable before autonomous control means anything.
5. HLG AC input is 120V = lethal. Blue/white dim wires are low-voltage and safe. GFCI on the AC side.

---

## What's on hand — electronics

| Item | Model / value | Status |
|------|---------------|--------|
| Raspberry Pi 5 | Model B Rev 1.1, 8GB | **live**, systemd service |
| ESP32 DevKit V1 | ≥2 on hand | one is the (flaky) light board |
| LED driver | Mean Well HLG-320H-48B (Type B, PWM dim) | wired to light board, flaky joint |
| pH sensor | Atlas Scientific EZO pH + isolated carrier | on hand — I2C 0x63 ⚠️ (bus was empty 5/14) |
| EC sensor | Atlas Scientific EZO-EC + carrier | on hand, **not wired** — expected at 0x64 |
| DO sensor | Atlas Scientific DO probe (yellow cap) + electrolyte | probe **on hand** (photo 5/12); EZO-DO circuit/carrier ⚠️ **ordered — confirm arrival** — expected at 0x61 |
| ADC | Adafruit ADS1115 | on hand — for **analog TDS** path (default I2C 0x48) |
| Temp probe | DS18B20 waterproof | live — 1-Wire on GPIO4 |
| Relay (main) | Digital Loggers IoT Relay II | wired to GPIO23 — **single input, ganged** |
| Relay (2nd) | DLI IoT Relay | ⚠️ on hand? confirm — candidate for the split |
| Relay (candidate) | Sainsmart multi-channel board | candidate to solve ganging |
| Transistor | 2N2222 NPN | in the PWM dim circuit |
| Resistor | 1kΩ (base current limit) | in the PWM dim circuit |
| Perfboard | EPLZON | the build substrate |
| Female pin headers | for socketing ESP32 | ⚠️ **needed for rebuild — confirm on hand or order** |
| 3D printer | Bambu Lab (PETG) | for enclosures / mounts / standoffplates |

---

## Sensor bus map (target)

- **I2C (shared bus, Atlas carriers, no ADC needed):** pH `0x63`, EC `0x64`, DO `0x61`.
- **TDS:** analog sensor → **ADS1115** (I2C `0x48`) → Pi. (TDS ≠ EC — different hardware path.)
- **1-Wire:** DS18B20 on **GPIO4**.
- ⚠️ **I2C bus 1 read EMPTY on last check (2026-05-14).** Carriers came off during the rebuild.
  Reconnect and run `i2cdetect -y 1` before trusting any address above.

---

## What's been tried / learned (the failures are the useful part)

**Light PWM controller — cold solder joint (open)**
- Breadboard version verified working Dec 2025 (Arduino Pin 9, inverted PWM: 0=full bright, 255=min).
- Migrated to ESP32 perfboard, soldered May 1. Layout: resistor C3–C9, transistor E-B-C in D2-D3-D4, WHITE(Dim−) E2, BLUE(Dim+) E4. Zero solder bridges — row connections do all routing.
- **May 12 FINAL diagnosis: cold solder joint.** Lights flicker when the board is physically grabbed. Boot banner absent on EN/RST press → possibly a bad TX line too. **Software path verified good** (light_controller.py + ESP32 firmware). No code fix possible.
- **Fix:** full perfboard rebuild with the ESP32 **socketed** (female headers), clean joints, re-verify TX.

**Relay ganging — design flaw (open)**
- DLI IoT Relay II has a **single GPIO input**: pump / heater / light / fan cannot be independently scheduled. Toggling the heater moves the pump.
- **Fix:** Sainsmart multi-channel relay board OR per-device smart plugs. This unblocks autonomous control.

**IR LED (mini-split control side track)**
- Black-body 940nm IR LEDs are **DOA** — clear-body only for IR emit. (Target was a Fujitsu Halcyon mini-split IR blaster.)

**Device-path fragility**
- ESP32 USB-serial device renumbers after any hiccup. A stale *regular file* once got created at `/dev/ttyUSB0` and blocked the kernel from making the real node.
- Set `stty 115200 raw -echo` before serial writes.
- ⚠️ Confirm the actual path on the Pi (`ttyUSB0` vs `ttyACM0` vs `/dev/serial/by-id/...`) — don't assume.

**EPLZON perfboard specifics**
- Rows connect horizontally. The center gap between columns **E and F has no electrical connection**.
- Components go in columns **B–E**. ESP32 headers go in **col A** and **col I**.
- Zero-jumper layout (route everything through row connections) is the right approach when it works.

---

## Open circuit work — priority order (conveyor belt, not buffet)

1. **Rebuild the light controller perfboard.** Socketed ESP32 (female headers), clean joints, verify TX. Re-test with `SET_BRIGHTNESS:xx` over serial.
2. **Split pump & heater** onto independent channels (Sainsmart 4-ch relay OR two smart plugs). Frees real autonomous control.
3. **Consolidated sensor board.** ~10×15cm perfboard hosting pH + EC + DO Atlas carriers + ADS1115, with screw terminals for power / I2C / analog, panel-mount BNC/SMA for probe cables, M3 + nylon standoffs, in a waterproof enclosure mounted outside the tent. (Concept already sketched — brain capture 2026-05-12.)
4. **Wire EC (0x64) + DO (0x61)** onto the bus as part of #3.
5. **Wire the analog TDS sensor** through the ADS1115.

---

## Repo / firmware (⚠️ confirm exact paths on the Mac before use)

- Repo: `~/dev/aquaponic-ai-system/` ⚠️ (older docs say `~/projects/AquaponicAISystem` — **reconcile**).
- ESP32 firmware: `esp32/hlg_light_controller/hlg_light_controller.ino`
- Pi control: `light_controller.py`, rules-engine YAML, SQLite `hydroponics.db`.
- GitHub: `github.com/killercatfish/AquaponicAISystem`
- Reference doc already in project: `Arduino_Breadboard_PWM_Dimmer_Layout.md` — this is the **gold-standard format** (layout diagram → placement → electrical path → pre-power multimeter tests → BOM → troubleshooting → safety). New board docs should match it.
