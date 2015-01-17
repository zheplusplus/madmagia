import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Maker(FileSystemEventHandler):

    def on_modified(self, _):
        Maker.lock = True
        print 'make'
        p = subprocess.Popen('make')
        p.wait()


def main():
    obs = Observer()
    obs.schedule(Maker(), path=os.path.dirname(__file__), recursive=True)
    obs.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()

if __name__ == '__main__':
    main()
