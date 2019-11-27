import threading
from interface.API import MCI
WAIT_SECONDS = 240


def request_token():
    MCI.token()
    try:
        threading.Timer(WAIT_SECONDS, request_token).start()
    except:
        pass
request_token()