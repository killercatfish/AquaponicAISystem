# CLAUDE_CONTEXT.md — Read This First
*Last updated: March 27, 2026*

## What This Project Is

Aquaponics monitoring and control system running on a Raspberry Pi 5. FastAPI backend, WebSocket dashboard, sensor integration, SQLite logging. Part of a larger basement lab project: cannabis DWC grow, NFT lettuce towers, 120-gallon fish tank, FarmBot for outdoor beds.

GitHub: https://github.com/killercatfish/AquaponicAISystem

## Access

| What | How |
|------|-----|
| Pi SSH | `ssh aquapi` (Tailscale IP: 100.117.109.76, user: pi, key auth) |
| Dashboard | http://100.117.109.76:8000 |
| Repo on Pi | ~/AquaponicAISystem |
| Virtual env | `source ~/AquaponicAISystem/venv/bin/activate` |
| Start app | `python -m src.hydroponics.core.main` |
| Brain API | brain.killercatfish.com |

## Hardware — What's Connected

| Sensor | Status | Address/Path | Notes |
|--------|--------|-------------|-------|
| Atlas Scientific EZO pH | LIVE | I2C 0x63 | On isolated carrier board (purple, Version 6). Wired to Pi GPIO extension board on breadboard. VCC→3.3V, GND→GND, SDA→GPIO2, SCL→GPIO3. Board set to I2C mode (configured via Arduino in earlier session). |
| DS18B20 Temperature | LIVE | /sys/bus/w1/devices/28-09b40087460f/temperature | 1-Wire on GPIO4. Reads raw int, divide by 1000 for °C. Reading ~19°C basement ambient. |
| Atlas EC (0x64) | NOT CONNECTED | Mock mode | No physical sensor |
| Atlas DO (0x61) | NOT CONNECTED | Mock mode | No physical sensor |
| Water level (HC-SR04) | NOT CONNECTED | Mock mode | GPIO pin conflict with relay |
| Relays | NOT CONNECTED | Mock mode | gpiozero needs lgpio/RPi module |

## Software Architecture

```
src/hydroponics/
├── core/main.py          # FastAPI app, WebSocket, scheduler, API endpoints
├── sensors/interfaces.py # AtlasSensors (I2C), TemperatureSensors (sysfs), WaterLevel, RelayControl
├── analysis/             # ParameterAnalyzer, TrendAnalyzer (needs data)
├── database/manager.py   # SQLite logging (data/databases/hydroponics.db)
├── ml/vision.py          # TFLite plant health (mock mode)
├── llm/interface.py      # LLM chat (mock mode)
templates/dashboard.html  # Full dashboard UI with WebSocket, charts, AKBS integration
```

## Key Technical Details

- **atlas_i2c v0.3.1**: Import from `atlas_i2c.atlas_i2c import AtlasI2C` (not top-level). `read('R')` requires command arg. Response: `r.data` is bytes, `r.status_code == 1` is success. Decode with `float(r.data.decode())`.
- **DS18B20**: No library needed. `glob.glob('/sys/bus/w1/devices/28-*/temperature')`, read file, int / 1000 = °C.
- **Scheduler**: APScheduler reads sensors every 30 seconds, automation every 60 seconds. Single instance (fixed March 27 2026 — was double-importing via uvicorn string).
- **First read after startup**: pH returns empty string on first cycle (sensor needs warmup after init). Not critical — all subsequent reads work.
- **AKBS Knowledge Base**: ChromaDB vector store with 5,354 chunks from RAS textbook. Separate repo: ~/aquaponics-knowledge-base-system. Integrated into dashboard info buttons and system analysis.

## Known Issues

1. First pH read after startup returns empty string (timing — sensor not ready). Low priority.
2. gpiozero can't load pin factory without lgpio/RPi modules. Blocks water level sensor and relay control. Need `pip install lgpio` or run as root.
3. EC and DO sensors don't exist physically — mock mode is correct behavior.
4. App spawns deprecation warnings for `on_event` — should migrate to lifespan handlers. Cosmetic.

## What's NOT in This Repo

- **aquaponics-knowledge-base-system** (~/aquaponics-knowledge-base-system on Pi) — ChromaDB + ingest pipeline. 3 commits.
- **Physical hardware**: 2x4 grow tent with LED, NFT tower system, 120-gal fish tank, FarmBot (disassembled), HLG-320H-48B LED driver with PWM dim wires.
- **Brain system**: brain.killercatfish.com — capture/digest system on VPS.

## Git History (Recent)

```
248aea7 Fix duplicate app instance: pass app object to uvicorn, move scheduler to startup event
ed88249 Independent per-sensor mock flags so one failed sensor doesn't disable all
2a84994 Fix real sensor integration: atlas_i2c import path, read API, direct sysfs temp
3472eda Fix temperature sensor display and API status endpoint
```

## Workflow

- **Planning/architecture/hardware**: Claude chat (Basement Lab project)
- **Code changes**: Claude Code on Mac → push to GitHub → git pull on Pi → restart app
- **Data logging**: Brain captures at end of sessions. Format: `brain capture "TYPE | domain | content"`
- **Physical next action**: Empty the grow tent. Then 2 DWC buckets in tent with cannabis.
