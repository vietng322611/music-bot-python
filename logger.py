# This made by vietng322611, please respect, do not copy without permission, you can change the code inside to your own.

from datetime import datetime
from sys import stdout

class logger:
    def __init__(self, f):
        self.file = f
        self.log = open(self.file["Log_Path"] + 'log-' + str(datetime.now().date()) + '@' + str(datetime.now().strftime('%H.%M.%S')) + '.txt', 'w')
        self.log.write('============================================\n')

    def flush(self):
        pass

    def write(self, text):      
        text = text.rstrip()
        if text != '':
            try:
                stdout.write('%s\n' % (text))
                self.log.write('%s\n' % (text))
            except UnicodeEncodeError:
                return
        return