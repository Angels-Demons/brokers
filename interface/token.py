import threading
from interface.API import MCI
WAIT_SECONDS = 240


def foo():
    MCI.token()
    threading.Timer(WAIT_SECONDS, foo).start()

foo()