import sys

class iterbar:
    def __init__(self, iterable, bar_length=20, task=None):
        self.iterable = iterable
        self.bar_length = bar_length
        self.total = len(iterable)
        self.current = 0
        self.task = task

    def __iter__(self):
        return self

    def __next__(self):
        if self.current < self.total:
            self.current += 1
            progress = self.current / self.total
            filled_length = int(self.bar_length * progress)
            bar = '#' * filled_length + '-' * (self.bar_length - filled_length)
            sys.stdout.write((str(self.task)+" " if self.task is not None else "")+f'[{bar}] {progress * 100:.2f}%\r')
            sys.stdout.flush()
            return self.iterable[self.current - 1]
        else:
            sys.stdout.write('\nDone!\n')
            sys.stdout.flush()
            raise StopIteration

if __name__ == "__main__":
    for i in iterbar(range(100000), task="Loading"):
        ...