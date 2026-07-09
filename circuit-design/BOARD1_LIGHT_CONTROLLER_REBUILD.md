# BOARD 1 — Light Controller Rebuild (Socketed ESP32)

**Replaces:** the May 1 perfboard (cold solder joint under direct-soldered ESP32 — final diagnosis 2026-05-12).
**Goal:** same proven circuit, ESP32 in female-header sockets, clean joints, TX verified.
**Driver:** Mean Well HLG-320H-48B (Type B, PWM dim). **Firmware:** `esp32/hlg_light_controller/hlg_light_controller.ino` (unchanged — software path verified good).
**Substrate:** EPLZON perfboard. Rows connect horizontally A–E and F–I(J); the E|F center gap is open.

---

## ⚡ SAFETY — read before touching anything

- The HLG's **AC input side is 120V and lethal**. Never touch driver wiring with the circuit energized. Kill it at the breaker/plug, verify dead, then work.
- Only the **BLUE (Dim+) and WHITE (Dim−)** wires are low-voltage (≤10V) and safe to handle.
- AC side runs through a **GFCI outlet** — this is a basement water environment.
- Strain-relieve the BLUE/WHITE wires on the board (below). A tugged wire on a marginal joint is exactly the failure being fixed.

---

## Design change vs. the as-built board — why the circuit moves

The as-built layout (resistor C3–C9, transistor E-B-C in D2-D3-D4, WHITE E2, BLUE E4) worked because only **two** ESP32 wires touched the board (GND→row 2, GPIO18→row 9). Rows 3 and 4 had no ESP32 connection.

**Socketing changes the netlist.** A full 15-pin header in col A puts an ESP32 pin on *every* row 1–15:

- Row 3 net would gain **GPIO15** (boot-strap pin) → tied straight to the transistor base. Light forced toward minimum during every boot; strap corrupted.
- Row 4 net would gain **GPIO2** (boot-strap pin) → tied to the collector / HLG Dim+, which the driver holds near **10V**. Out of absolute-max for any ESP32 pin. Chip damage.

**Fix:** module occupies rows 1–15; the transistor circuit moves to rows 17–19, fed by two short insulated jumpers (GND from row 2, GPIO18 from row 9). Zero-jumper doesn't survive socketing — two jumpers is the honest cost. Same component pattern otherwise.

---

## What's verified vs. what you must confirm

| # | Item | Status |
|---|------|--------|
| 1 | PWM pin = **GPIO18**, 1 kHz, 8-bit, inverted logic | ✅ verified in `hlg_light_controller.ino` |
| 2 | Serial protocol `SET:pct` / `GET` / `FADE:pct:secs` / `TEST`, 115200 baud, `\n` | ✅ verified in firmware + `light_controller.py` (it is **not** `SET_BRIGHTNESS:`) |
| 3 | Pi opens `/dev/ttyUSB0` by default, parks DTR/RTS after open | ✅ verified in `src/hydroponics/sensors/light_controller.py` |
| 4 | As-built layout + EPLZON row behavior | ✅ per `esp32/LIGHT_CONTROLLER.md` (board is gone; convention retained) |
| 5 | Which of the 2 ESP32s has healthy USB/TX | ⚠️ **bench-test bare on the Mac** (step 0 below) — the old board's missing boot banner may be a dead TX |
| 6 | Female 15-pin headers on hand | ⚠️ confirm or order (BOM) |
| 7 | Module width vs. board columns (col A ↔ col I or J) | ⚠️ **dry-fit before soldering.** The right column's exact letter is electrically irrelevant (no nets used on that side) |
| 8 | Pin-to-row map: GND lands row 2, GPIO18 (D18) lands row 9 | ⚠️ verify against **silkscreen** at dry-fit. Typical DevKit V1 has GND 2nd and D18 9th on the 3V3-side column, matching the old build — but trust the silkscreen, not this doc. If they land elsewhere, move the two jumper taps to the actual GND/D18 rows; nothing else changes |
| 9 | Perfboard piece has ≥ 21 usable rows | ⚠️ confirm (module 15 + circuit through row 21) |
| 10 | Actual serial path on the Pi after rebuild | ⚠️ `ls -l /dev/serial/by-id/` on aquapi with board plugged in |

---

## 1. Perfboard layout (EPLZON convention)

Cols A–I(J) across, rows 1–21 down. Rows connect A–E and F–I; `|` = open center gap. Col A/I labels are the **typical DevKit V1** pin map — item 8 above, verify silkscreen. Orient the module so **GND sits in row 2 and D18 in row 9**.

```
      A      B     C     D     E   |   F     G     H     I
 1  [3V3]    .     .     .     .   |   .     .     .   [EN ]
 2  [GND]  J1in    .     .     .   |   .     .     .   [VP ]
 3  [D15]    .     .     .     .   |   .     .     .   [VN ]
 4  [D2 ]    .     .     .     .   |   .     .     .   [D34]
 5  [D4 ]    .     .     .     .   |   .     .     .   [D35]
 6  [RX2]    .     .     .     .   |   .     .     .   [D32]
 7  [TX2]    .     .     .     .   |   .     .     .   [D33]
 8  [D5 ]    .     .     .     .   |   .     .     .   [D25]
 9  [D18]  J2in    .     .     .   |   .     .     .   [D26]
10  [D19]    .     .     .     .   |   .     .     .   [D27]
11  [D21]    .     .     .     .   |   .     .     .   [D14]
12  [RX0]    .     .     .     .   |   .     .     .   [D12]
13  [TX0]    .     .     .     .   |   .     .     .   [D13]
14  [D22]    .     .     .     .   |   .     .     .   [GND]
15  [D23]    .     .     .     .   |   .     .     .   [VIN]
16    .      .     .     .     .   |   .     .     .     .
17  (10k)  J1out   .    Etr   W−   |   .    (SR)   .     .
18  (10k)    .    R●    Bas    .   |   .     .     .     .
19    .      .     .    Col   B+   |   .    (SR)   .     .
20    .      .     .     .     .   |   .     .     .     .
21    .    J2out  R●     .     .   |   .     .     .     .
```

- `J1` = GND jumper (B2 → B17). `J2` = GPIO18 jumper (B9 → B21). Insulated solid-core, routed on the top side.
- `R●` = 1 kΩ resistor, vertical mount, spanning C21 → C18.
- `Etr/Bas/Col` = 2N2222 emitter / base / collector in D17 / D18 / D19.
- `W−` = HLG WHITE (Dim−) at E17. `B+` = HLG BLUE (Dim+) at E19.
- `(SR)` = strain relief: pass each HLG wire through G17/G19 (F-side nets, unused, insulation intact, **no solder**) before it crosses the gap to its E-column solder hole.
- `(10k)` = optional base pull-down, A17 → A18 (see BOM).

## 2. Component placement details

| Component | Holes | Orientation / notes |
|---|---|---|
| Female header, 15-pin | A1–A15 | Solder side. Seat the header **on the ESP32's pins**, place the whole assembly on the board, then tack pins 1 and 15 first, re-check squareness, solder the rest. Prevents misaligned sockets. |
| Female header, 15-pin | I1–I15 (or J — dry-fit) | Same procedure, same time as col A header. Purely mechanical + power-side pins; no circuit nets on this side. |
| Jumper J1 (GND) | B2 → B17 | Insulated solid-core, top side, flat against board. |
| Jumper J2 (GPIO18) | B9 → B21 | Same. |
| 1 kΩ resistor | C21 (top) → C18 (bottom) | Vertical mount: body standing at C18, long leg folded down into C21. |
| 2N2222 | E→D17, B→D18, C→D19 | TO-92 **flat face toward col A**, legs fanned to consecutive rows — same physical orientation as the proven as-built board. ⚠️ If using a different brand/batch than the December breadboard part, confirm E-B-C pinout on its datasheet — some 2N2222 packages are C-B-E. The diode check in §4 catches a swap. |
| HLG WHITE (Dim−) | E17 | Strip ~4 mm, through-hole from top, solder, then **tug-test**. |
| HLG BLUE (Dim+) | E19 | Same. |
| 10 kΩ (optional) | A17 → A18 | Base pull-down. Guarantees the transistor stays off (light = full bright) while GPIO18 floats during boot/reflash. Recommended if a 10 k is on hand; circuit works without it. |

Board practice for this rebuild (the failure was a joint, not the design): flux on every pad, 63/37 if available, inspect every joint with magnification for the volcano fillet, and physically tug every wire and wiggle the transistor before power. Label the board with date + `GPIO18 / SET:0-100`.

## 3. Electrical path verification (hole-to-hole)

- **PWM drive:** ESP32 GPIO18 pin (A9) ─row 9─ J2 in at B9 → jumper → B21 ─row 21─ resistor top C21 → 1 kΩ → resistor bottom C18 ─row 18─ base D18. ✔ GPIO → 1 k → base.
- **Ground:** ESP32 GND pin (A2) ─row 2─ J1 in at B2 → jumper → B17 ─row 17─ emitter D17 and WHITE E17. ✔ Emitter and Dim− at GND.
- **Dim line:** BLUE E19 ─row 19─ collector D19. ✔ Collector pulls Dim+ to Dim− when driven.
- **Isolation:** rows 17/18/19 sit below the module — no ESP32 pin shares them (holes A17/A18 only carry the optional 10 k). Rows 16 and 20 are empty guard rows. The E|F gap isolates the strain-relief holes. No net touches a boot-strap pin.
- **Logic (inverted, handled in firmware):** duty 0 → transistor off → Dim+ floats → full bright. Duty 255 → transistor saturated → Dim+ ≈ GND → minimum (~10%, HLG Type B does not switch fully off).

## 4. Pre-power multimeter checklist

Module **out of socket**, HLG **disconnected**, board unpowered. All refs are hole positions.

| # | Test | Meter | Expect |
|---|------|-------|--------|
| 1 | Strip sanity: A2 ↔ E2 | continuity | beep (one row = one net) |
| 2 | Gap: E17 ↔ F17 | continuity | **open** |
| 3 | J1: B2 ↔ D17 and B2 ↔ E17 | continuity | beep |
| 4 | J2: B9 ↔ B21 | continuity | beep |
| 5 | GPIO→base path: B9 ↔ D18 | Ω | ≈ 1.0 kΩ |
| 6 | Base–emitter: red D18, black D17 | diode | 0.6–0.7 V |
| 7 | Base–collector: red D18, black D19 | diode | 0.6–0.7 V |
| 8 | Emitter ↔ collector: D17 ↔ D19, both polarities | diode | OL both ways (a short here puts the light at permanent minimum; a reading in one direction means E/C swapped) |
| 9 | WHITE ↔ BLUE: E17 ↔ E19 | continuity | open |
| 10 | Header bridges: every adjacent pair A1↔A2 … A14↔A15, and same on col I — **except** skip interpreting A17-area; this is the most likely bridge location on the whole board | continuity | all open |
| 11 | Row 2 ↔ row 3 and row 9 ↔ row 10 (bridge check at the jumper taps) | continuity | open |
| 12 | Module seated: 3V3 pin (A1) ↔ GND pin (A2) | Ω | kΩ or higher — **not** 0 (a short here cooks the Pi's USB port) |

## 5. BOM

| Qty | Part | Value | Note |
|-----|------|-------|------|
| 1 | ESP32 DevKit V1, 30-pin | — | on hand (×2) — **use whichever passes the step-0 banner test** |
| 2 | Female pin header, 1×15, 2.54 mm | — | ⚠️ **confirm on hand or order** (cutting 1×40 strips to 15 is fine) |
| 1 | 2N2222 NPN, TO-92 | — | on hand |
| 1 | Resistor, ¼ W | 1 kΩ | on hand (salvage from old board or spare) |
| 1 | Resistor, ¼ W (optional) | 10 kΩ | base pull-down — ⚠️ confirm on hand; skip if not |
| ~10 cm | Solid-core insulated wire | 22 AWG | for J1/J2 — ⚠️ confirm |
| 1 | EPLZON perfboard piece | ≥ 21 rows | ⚠️ confirm the piece is long enough |
| — | Flux pen, 63/37 solder | — | recommended given the cold-joint history |

## 6. Power-up sequence + expected behavior

**Step 0 — no bench needed, do now (Mac + micro-USB data cable):** bare-module banner test on **both** ESP32s.
```
ls /dev/cu.usbserial*          # find the port
screen /dev/cu.usbserial-XXXX 115200   # then press the EN button on the module
```
Expect the ROM boot text (`rst:0x1 ... ets Jul 29 2019` etc.) on EN press. A module with no banner has a dead TX/USB-UART path — that's possibly what the old board's symptom was. Build with a module that passes. (`Ctrl-A k` exits screen.)

1. Flash the winning module with `TEST_MODE true` (board type `ESP32 Dev Module`).
2. Build the board; run the full §4 checklist. Fix anything before proceeding.
3. Seat the module. USB from the **Mac**, HLG still disconnected. Expect `HLG LIGHT CONTROLLER READY` then the test cycle log. Send `SET:0` → meter DC at D18 (base) vs D17 reads ≈ 0.6–0.7 V; `SET:100` → ≈ 0 V. That's the drive path proven with zero AC involved.
4. **AC step.** Driver unpowered at the breaker/plug. Connect WHITE→E17 pigtail, BLUE→E19, strain relief through G17/G19. Power up through the GFCI. `TEST` → light steps 100 → 75 → 50 → 25 → 10% → fades back. Note: minimum is ~10%, not off — Type B behavior, correct.
5. **Wiggle test — this is the acceptance test for the rebuild.** Light at 50%. Grab the board, flex it gently, tap the module and each wire. Zero flicker allowed. Press EN → boot banner must appear every time (TX verified).
6. Reflash `TEST_MODE false`. Mount high in the tent, 15-ft USB down to the Pi. On aquapi: `ls -l /dev/serial/by-id/` → note the stable path (device renumbering + the stale-file-at-`/dev/ttyUSB0` incident make the by-id path the one to configure).
7. End-to-end: `stty -F /dev/serial/by-id/<path> 115200 raw -echo`, then `echo "SET:75" > <path>` and confirm `OK:BRIGHTNESS:75` (or run it through `light_controller.py`). Done when `GET` round-trips from the Pi.

## 7. Troubleshooting

| Symptom | Likely cause | Check / fix |
|---|---|---|
| No boot banner on EN (Mac) | Dead USB-UART on module, or charge-only cable | Swap cable first, then module — step 0 exists to catch this before building |
| Banner OK but `ERR:UNKNOWN:...` | Line-ending / echo garbage | `stty ... raw -echo` before writing; commands end `\n` only |
| Light permanently full bright, ignores SET | Base drive path open — J2, resistor joint, or base joint cold | §4 test 5 (B9↔D18 ≈ 1 kΩ); meter base voltage during `SET:0` (want 0.6–0.7 V) |
| Light permanently at minimum | Collector–emitter short (bridge row 17↔19) or E/C swapped | §4 tests 8 & 9; transistor orientation |
| Flicker when board touched | Cold joint (the original failure) | Reflow every joint with flux; repeat wiggle test |
| Dimming direction feels reversed | WHITE/BLUE swapped | WHITE (Dim−) must be on the GND/emitter row 17; BLUE on collector row 19 |
| Worked on Mac, dead from Pi | Port renumbered, or stale regular file at `/dev/ttyUSB0` | `ls -l /dev/serial/by-id/`; `file /dev/ttyUSB0` must say *character special*, not *regular file* — delete the stale file if present |
| ESP32 won't boot / boots to garbage when seated | Something re-tied to a strap pin (GPIO0/2/5/12/15) | Verify nothing but header pins occupy rows 1–15; recheck for bridges at A3/A4/A8 |

---

## Meantime (no soldering required)

1. **Step 0 banner test** on both modules — only needs the Mac and a USB cable. Decides the BOM.
2. Confirm/order **female headers** (BOM item 2) — the only likely missing part.
3. After rebuild, switch the configured port to the `/dev/serial/by-id/` path (constructor already takes `port=`; it's a config change, not a code change).
