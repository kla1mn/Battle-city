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

    def update(self):
        for timer in self.timers:
            timer["time"] += 1
            if timer["time"] >= timer["interval"]:
                timer["time"] = 0
                timer["callback"]()
                timer["times"] += 1
                if -1 < timer["repeat"] <= timer["times"]:
                    self.timers.remove(timer)
