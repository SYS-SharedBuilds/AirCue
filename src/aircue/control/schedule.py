"""School operational schedule and timetable outdoor activity filter."""
from __future__ import annotations

from datetime import datetime, time
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

from aircue.config import ScheduleConfig


class SchoolSchedule:
    """Manages school operational windows and timetable slots."""

    def __init__(self, config: Optional[ScheduleConfig] = None, timezone: str = "Asia/Kolkata") -> None:
        self.config = config or ScheduleConfig()
        self.tz = ZoneInfo(timezone)

        # Parse start and end operational times
        s_parts = [int(p) for p in self.config.start_time.split(":")]
        e_parts = [int(p) for p in self.config.end_time.split(":")]
        self.start_t = time(s_parts[0], s_parts[1])
        self.end_t = time(e_parts[0], e_parts[1])

    def is_school_hours(self, dt: datetime) -> bool:
        """Return True if given datetime is within school operating hours and not a holiday."""
        # Normalize timezone
        if dt.tzinfo is None:
            local_dt = dt.replace(tzinfo=self.tz)
        else:
            local_dt = dt.astimezone(self.tz)

        # Check weekday (0 = Monday, 6 = Sunday)
        if local_dt.weekday() not in self.config.school_days:
            return False

        # Check holiday list
        date_str = local_dt.strftime("%Y-%m-%d")
        if date_str in self.config.holidays:
            return False

        # Check time bounds
        curr_t = local_dt.time()
        return self.start_t <= curr_t <= self.end_t

    def get_current_slot(self, dt: datetime) -> Optional[str]:
        """Return identifier of active outdoor timetable slot (e.g. 'assembly', 'sports_pt')."""
        if not self.is_school_hours(dt):
            return None

        if dt.tzinfo is None:
            local_dt = dt.replace(tzinfo=self.tz)
        else:
            local_dt = dt.astimezone(self.tz)

        curr_t = local_dt.time()
        for slot_key, slot in self.config.outdoor_slots.items():
            s_parts = [int(p) for p in slot.start.split(":")]
            e_parts = [int(p) for p in slot.end.split(":")]
            st_val = time(s_parts[0], s_parts[1])
            et_val = time(e_parts[0], e_parts[1])
            if st_val <= curr_t <= et_val:
                return slot_key

        return None
