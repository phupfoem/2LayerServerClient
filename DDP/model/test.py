from threading import Thread, Event, Lock
from time import sleep
varl = 0
data_lock = Lock()


def foo():
    while True:
        with data_lock:
            print("hello", varl)
        sleep(1)


def goo():
    while True:
        with data_lock:
            print("hi")
            global varl
            varl += 1
            print("foo", varl)
        sleep(2)


thread1 = Thread(target=foo)
thread2 = Thread(target=goo)
if not thread1.is_alive():
    thread1.start()
if not thread2.is_alive():
    thread2.start()
