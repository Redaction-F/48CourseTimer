import time
from typing import Self, Optional
from enum import Enum

class Time:
    uppers = [100, 60, 60, 100]
    rems = [360000, 6000, 100, 1]

    def __init__(self, csec: int):
        self.__is_plus : bool
        if csec >= 0:
            self.__is_plus = True
        else:
            self.__is_plus = False
            csec = -csec
        self.__hour: int = csec // 360000
        self.__minute: int = (csec // 6000) % 60
        self.__sec: int = (csec // 100) % 60
        self.__csec: int = csec % 100

    @classmethod
    def from_input(cls, hour: str, minute: str, sec: str, csec: str) -> Optional[Self]:
        csec_res: int = 0
        for (s, (u, v)) in zip([hour, minute, sec, csec], zip(Time.uppers, Time.rems)):
            if s.isdecimal():
                int_s: int = int(s)
                if 0 <= int_s < u:
                    csec_res += int_s * v
                else:
                    return None
            else:
                return None
        return Time(csec_res)

    def to_str(self, display_pm: bool=False) -> str:
        if display_pm:
            if self.__is_plus:
                return "+{:0>2}:{:0>2}.{:0>2}".format(self.__minute, self.__sec, self.__csec)
            else:
                return "-{:0>2}:{:0>2}.{:0>2}".format(self.__minute, self.__sec, self.__csec)
        else:
            return "{:0>2}:{:0>2}:{:0>2}.{:0>2}".format(self.__hour, self.__minute, self.__sec, self.__csec)
    
    @property
    def time_list(self) -> list[int]:
        return [self.__hour, self.__minute, self.__sec, self.__csec]

    @property
    def hour(self) -> int:
        return self.__hour
    
    @property
    def minute(self) -> int:
        return self.__minute
    
    @property
    def sec(self) -> int:
        return self.__sec
    
    @property
    def csec(self) -> int:
        return self.__csec
    
    @property
    def total_csec(self) -> int:
        return (1 if self.__is_plus else -1) * sum(map(lambda x: x[0] * x[1], zip(self.time_list, Time.rems)))
    
    def __add__(self, other: Self) -> Self:
        return Time(self.total_csec + other.total_csec)

    def __sub__(self, other: Self) -> Self:
        return Time(self.total_csec - other.total_csec)

class TimerMode(Enum):
    STOP_MODE = 0
    INTERRUPT_MODE = 1
    RUN_MODE = 2


class Timer:
    def __init__(self):
        self.__start_time: float = 0.0
        self.__interrupt_time: float = 0.0
        self.__pre_lap_time: float = 0.0
        self.__state: TimerMode = TimerMode.STOP_MODE
    
    def __repr__(self) -> str:
        return self.time.to_str()
    
    @property
    def time(self) -> Time:
        passed_time: int
        if self.__state == TimerMode.STOP_MODE:
            passed_time = 0
        elif self.__state == TimerMode.INTERRUPT_MODE:
            passed_time = int((self.__interrupt_time - self.__start_time) * 100)
        else:
            passed_time = int((time.time() - self.__start_time) * 100)
        return Time(passed_time)
    
    def start_restart_stop(self):
        now: float = time.time()
        if self.__state == TimerMode.STOP_MODE:
            # Start
            self.__start_time = now
            self.__pre_lap_time = now
            self.__state = TimerMode.RUN_MODE
        elif self.__state == TimerMode.INTERRUPT_MODE:
            # Restart
            self.__start_time += now - self.__interrupt_time
            self.__pre_lap_time += now - self.__interrupt_time
            self.__state = TimerMode.RUN_MODE
        else:
            # Stop
            self.__interrupt_time = now
            self.__state = TimerMode.INTERRUPT_MODE
    
    def stop(self):
        if self.__state == TimerMode.RUN_MODE:
            now: float = time.time()
            self.__interrupt_time = now
            self.__state = TimerMode.INTERRUPT_MODE

    def reset(self):
        if self.__state == TimerMode.INTERRUPT_MODE:
            self.__start_time = 0.0
            self.__interrupt_time = 0.0
            self.__pre_lap_time = 0.0
            self.__state = TimerMode.STOP_MODE
    
    def lap(self) -> Optional[int]:
        if self.__state == TimerMode.RUN_MODE:
            now: float = time.time()
            lap: int = int((now - self.__pre_lap_time) * 100)
            self.__pre_lap_time = now
            return lap
        else:
            return None
    
    def button_labels(self) -> tuple[Optional[str], Optional[str], Optional[str]]:
        if self.__state == TimerMode.STOP_MODE:
            return (None, "Start", None)
        elif self.__state == TimerMode.INTERRUPT_MODE:
            return ("Reset", "Restart", None)
        else:
            return (None, "Stop", "Lap")