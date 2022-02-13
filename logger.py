from datetime import datetime
from sys import stdout

class logger:
    def __init__(self, f):
        self.file = f
        self.log = open(self.file["Log_Path"] + 'log-' + str(datetime.now().date()) + '@' + str(datetime.now().strftime('%H.%M.%S')) + '.txt', 'w')

    def flush(self):
        pass

    def write(self, text):
        text = text.rstrip()
        if text != '':
            try:
                stdout.write(f"[{datetime.now().strftime('%H.%M.%S')}]" + ' %s\n' % (text))
                self.log.write(f"[{datetime.now().strftime('%H.%M.%S')}]" + ' %s\n' % (text))
            except UnicodeEncodeError:
                return
        return