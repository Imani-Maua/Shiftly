from abc import ABC, abstractmethod
from app.entities.entities import talentAvailability, shiftSpecification
from datetime import date, datetime
from collections import defaultdict

class talentByRole():
    @staticmethod
    def group_talents(talents: list[talentAvailability]):
        talents_by_role = defaultdict(list)
        for talent in talents:
            talents_by_role[talent.role].append((talent.talent_id, talent.window, talent.shift_name))
        return talents_by_role


class talentAvailableWindow():
    def __init__(self, talents: list[talentAvailability]):
        self.talents = talents 

    def talent_window_lookup(self):
        window = defaultdict(list)
        for talent in self.talents:
            window[(talent.talent_id, talent.window[0].date())].append(talent.window) 
        return window


class talentAvailableShift():
    def __init__(self, talents: list[talentAvailability]):
        self.talents = talents

    def talent_shift_lookup(self):
        lookup = defaultdict(set)
        for talent in self.talents:
            for shift in talent.shift_name:
                lookup[(talent.talent_id, talent.window[0].date())].add(shift)
        return lookup


class dailyAssignmentTracker():

    def __init__(self):
        self.assigned = set()

    def mark_assigned(self, talent_id: int, shift_date: date):
        self.assigned.add((talent_id, shift_date))

    def check(self, talent_id: int, date: date) -> bool:
        return (talent_id, date) in self.assigned


class TalentGenerator():
    def __init__(self, shift: shiftSpecification, talents_by_role: dict[str, tuple[int, tuple]], lookup: dict[tuple[int, date], tuple[date, date]]):
        self.shift = shift
        self.talents_by_role = talents_by_role
        self.lookup = lookup

    def find_eligible_talents(self):
           seen = set()
           for talent_id, _, shifts in self.talents_by_role[self.shift.role_name]:
              window_lookup = self.lookup.get((talent_id, self.shift.start_time.date()), [])
              if any(start <= self.shift.start_time and end >= self.shift.end_time for start,end in window_lookup):
                  if self.shift.shift_name in shifts:
                    if talent_id not in seen:
                        yield talent_id
                        seen.add(talent_id)