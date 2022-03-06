from datetime import datetime
from sys import stdout
from sys import stderr

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
                if stdout:
                  stdout.write('%s\n' % (text))
                elif stderr:
                  stderr.write()
                self.log.write('%s\n' % (text))
            except UnicodeEncodeError:
                return
        return