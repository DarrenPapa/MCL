import psutil
import os
import time
from threading import Thread, Event

def memory_usage_psutil():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss

def monitor(max_memory, stop_event, resolution=1.2):
    while not stop_event.is_set():
        memory = memory_usage_psutil()
        if memory > max_memory[0]:
            max_memory[0] = memory
        time.sleep(resolution)  # change this for resolution

def monitor_memory(func):
    def wrapper(*args, **kwargs):
        max_memory = [0]
        stop_event = Event()
        monitor_thread = Thread(target=monitor, args=(max_memory, stop_event))
        monitor_thread.start()
        try:
            result = func(*args, **kwargs)
        finally:
            print("Done!")
            stop_event.set()
            print("Event sent\nWaiting for thread...")
            monitor_thread.join()
            print(f"Maximum memory usage: {max_memory[0] / (1024 ** 2):.2f} MB")
        return result
    return wrapper


def monitor_memory_highres(func):
    def wrapper(*args, **kwargs):
        max_memory = [0]
        stop_event = Event()
        monitor_thread = Thread(target=monitor, args=(max_memory, stop_event, 0))
        monitor_thread.start()
        try:
            result = func(*args, **kwargs)
        finally:
            print("Done!")
            stop_event.set()
            print("Event sent\nWaiting for thread...")
            monitor_thread.join()
            print(f"Maximum memory usage: {max_memory[0] / (1024 ** 2):.2f} MB")
        return result
    return wrapper

@monitor_memory
def my_function():
    # Your code here
    a = [i for i in range(100000)]
    b = [i * 2 for i in range(100000)]
    del a
    return b

if __name__ == "__main__":
    my_function()
