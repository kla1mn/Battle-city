import logging


class Timer:
    def __init__(self):
        self.timers = []

    def add(self, interval, callback, repeat=-1):
        self.timers.append({
            "interval": interval,
            "callback": callback,
            "repeat": repeat,
            "times": 0,
            "time": 0
        })

    def update(self, time_passed):
        timers_to_remove = []
        for timer in self.timers:
            timer["time"] += time_passed
            while timer["time"] >= timer["interval"]:
                timer["time"] -= timer["interval"]
                timer["times"] += 1
                try:
                    timer["callback"]()
                except Exception as e:
                    logging.error(f"Error in timer callback: {e}")
                    timers_to_remove.append(timer)
                    break

                if timer["repeat"] != -1 and timer["times"] >= timer["repeat"]:
                    timers_to_remove.append(timer)
                    break

        for timer in timers_to_remove:
            self.timers.remove(timer)
