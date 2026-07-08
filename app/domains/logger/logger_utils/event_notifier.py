from threading import Event

new_log_event = Event()

def notify_new_log():

    print("Event Set")
    new_log_event.set()


def wait_new_log():

    print("Wait Start")
    new_log_event.wait()

    print("Wait Finish")
    new_log_event.clear()