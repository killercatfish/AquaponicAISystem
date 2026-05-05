"""
Pump cycle controller — 1 min ON / 14 min OFF, 24/7 on the GPIO23 relay.

Manual override pauses the auto cycle until "Resume Auto" is invoked.
"""

import logging
from datetime import datetime
from typing import Dict

from apscheduler.schedulers.background import BackgroundScheduler

from hydroponics.sensors.interfaces import relay_control

logger = logging.getLogger(__name__)


class PumpCycleState:
    def __init__(self):
        self.mode = 'auto'  # 'auto' | 'manual'


pump_cycle = PumpCycleState()


def _is_on_minute(now: datetime) -> bool:
    """Cycle pattern: ON at minute 0,15,30,45 — OFF the other 14 minutes."""
    return now.minute % 15 == 0


def _pump_on_job():
    if pump_cycle.mode != 'auto':
        logger.info("Pump auto-cycle paused (manual mode), skipping ON")
        return
    logger.info("Pump auto-cycle: ON")
    relay_control.set_relay('pump', True)


def _pump_off_job():
    if pump_cycle.mode != 'auto':
        logger.info("Pump auto-cycle paused (manual mode), skipping OFF")
        return
    logger.info("Pump auto-cycle: OFF")
    relay_control.set_relay('pump', False)


def register_schedule(scheduler: BackgroundScheduler):
    """Register cron jobs: ON at *:00/15/30/45, OFF one minute later."""
    scheduler.add_job(
        _pump_on_job, 'cron',
        minute='0,15,30,45',
        id='pump_cycle_on',
        replace_existing=True,
    )
    scheduler.add_job(
        _pump_off_job, 'cron',
        minute='1,16,31,46',
        id='pump_cycle_off',
        replace_existing=True,
    )
    logger.info("Pump cycle registered: 1 min ON / 14 min OFF (24/7)")

    # Snap to current expected state on startup so we don't wait up to 15 min
    # for the cycle to assert itself.
    if pump_cycle.mode == 'auto':
        target = _is_on_minute(datetime.now())
        relay_control.set_relay('pump', target)
        logger.info(f"Pump cycle: boot-time state set to {'ON' if target else 'OFF'}")


def manual_on():
    pump_cycle.mode = 'manual'
    relay_control.set_relay('pump', True)
    logger.info("Pump set to manual ON")


def manual_off():
    pump_cycle.mode = 'manual'
    relay_control.set_relay('pump', False)
    logger.info("Pump set to manual OFF")


def resume_auto():
    """Switch back to auto cycle and snap to whichever state the cycle expects right now."""
    pump_cycle.mode = 'auto'
    target = _is_on_minute(datetime.now())
    relay_control.set_relay('pump', target)
    logger.info(f"Pump auto-cycle resumed, snapped to {'ON' if target else 'OFF'}")


def get_status() -> Dict:
    return {
        'mode': pump_cycle.mode,
        'state': bool(relay_control.get_state('pump')),
    }
