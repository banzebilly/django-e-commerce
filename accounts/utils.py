#using tread to send email in second
from threading import Thread

class EmailThread(Thread):
    def __init__(self, send_email):
        self.send_email = send_email
        super(EmailThread, self).__init__()

    def run(self):
        self.send_email.send()
 