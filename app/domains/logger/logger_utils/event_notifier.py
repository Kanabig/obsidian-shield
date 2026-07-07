from threading import Event

new_log_event = Event()

def notify_new_log():
    new_log_event.set()


def wait_new_log():

    new_log_event.wait()

    new_log_event.clear()