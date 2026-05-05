"""
Sunrise/sunset schedule for the HLG PWM dimmer.

Daily plan:
    on_hour:00         -> ramp 0 -> 100% over ramp_minutes
    on_hour:ramp end   -> hold at 100%
    off_hour:00        -> ramp 100 -> 0% over ramp_minutes
    off_hour:ramp end  -> hold at 0%

Schedule jobs are registered with APScheduler. Boot-time recovery uses
compute_target_brightness() to put the lamp where the schedule says it
should be right now (so app restarts don't strand the light at 100%).
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler

from hydroponics.sensors.light_controller import light_controller

logger = logging.getLogger(__name__)


def compute_target_brightness(
    now: datetime,
    on_hour: int,
    off_hour: int,
    ramp_minutes: int,
) -> int:
    """Return the brightness (0-100) the schedule expects at `now`."""
    sunrise_start = now.replace(hour=on_hour, minute=0, second=0, microsecond=0)
    sunrise_end = sunrise_start + timedelta(minutes=ramp_minutes)
    sunset_start = now.replace(hour=off_hour, minute=0, second=0, microsecond=0)
    sunset_end = sunset_start + timedelta(minutes=ramp_minutes)

    if now < sunrise_start:
        return 0
    if now < sunrise_end:
        progress = (now - sunrise_start).total_seconds() / (ramp_minutes * 60)
        return int(round(progress * 100))
    if now < sunset_start:
        return 100
    if now < sunset_end:
        progress = (now - sunset_start).total_seconds() / (ramp_minutes * 60)
        return int(round((1 - progress) * 100))
    return 0


def _sunrise_job(target_pct: int, duration_seconds: int):
    logger.info(f"Light schedule: starting sunrise ramp to {target_pct}% over {duration_seconds}s")
    light_controller.fade_to(target_pct, duration_seconds)


def _sunset_job(target_pct: int, duration_seconds: int):
    logger.info(f"Light schedule: starting sunset ramp to {target_pct}% over {duration_seconds}s")
    light_controller.fade_to(target_pct, duration_seconds)


def register_schedule(
    scheduler: BackgroundScheduler,
    on_hour: int,
    off_hour: int,
    ramp_minutes: int,
):
    """Register sunrise/sunset cron jobs and apply boot-time recovery."""
    duration_seconds = ramp_minutes * 60

    scheduler.add_job(
        _sunrise_job,
        'cron',
        hour=on_hour,
        minute=0,
        id='light_sunrise',
        replace_existing=True,
        kwargs={'target_pct': 100, 'duration_seconds': duration_seconds},
    )
    scheduler.add_job(
        _sunset_job,
        'cron',
        hour=off_hour,
        minute=0,
        id='light_sunset',
        replace_existing=True,
        kwargs={'target_pct': 0, 'duration_seconds': duration_seconds},
    )
    logger.info(
        f"Light schedule registered: sunrise {on_hour:02d}:00, "
        f"sunset {off_hour:02d}:00, ramp {ramp_minutes} min"
    )

    # Boot-time recovery: snap the lamp to whatever the schedule expects.
    target = compute_target_brightness(datetime.now(), on_hour, off_hour, ramp_minutes)
    light_controller.set_brightness(target)
    logger.info(f"Light schedule: boot-time brightness set to {target}%")
