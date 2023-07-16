from time import sleep
from tqdm import tqdm
import time


class RateLimitingModel:
    def __init__(self):
        self.list_call = []

    def seconds_to_next_call(self):
        current_time = time.time()
        # max of 3 call per minutes
        if len(self.list_call) < 3:
            return 0
        else:
            return 60 - (current_time - self.list_call[-3])

    def await_timer(self) -> None:
        seconds_to_sleep = self.seconds_to_next_call()
        centiseconds_to_sleep = int(seconds_to_sleep * 100)
        for _ in tqdm(range(centiseconds_to_sleep)):
            sleep(0.01)

    def call(self) -> None:
        current_time = time.time()
        self.list_call.append(current_time)
