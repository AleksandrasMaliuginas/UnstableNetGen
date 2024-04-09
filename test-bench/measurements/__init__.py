import time
import logging
from enum import Enum

log = logging.getLogger()


class AppCounters:
    def __init__(self, enumCounterDescriptor):
        self.counters: dict = {}

        for counter in enumCounterDescriptor:
            self.counters[counter.name] = None

    def report(self, counter: Enum, value):
        if counter.name in self.counters:
            self.counters[counter.name] = value
        else:
            log.warning(f"Counter {counter.name} not registered.")

    def reportDuration(self, counter: Enum, startTimeSec: float):
        if counter.name in self.counters:
            self.counters[counter.name] = round(time.time() - startTimeSec, 5)
        else:
            log.warning(f"Counter {counter.name} not registered.")

    def __str__(self) -> str:
        return str(self.counters)
