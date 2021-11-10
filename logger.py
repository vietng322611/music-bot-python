# This made by vietng322611, please respect, do not copy without permission, you can change the code inside to your own.

from datetime import datetime
from sys import stdout

class logger:
    config = {}
    def __init__(self, f):
        self.file = f
        self.log = open(self.file["Log_Path"] + 'log-' + str(datetime.now().date()) + '.txt', 'a')
    def flush(self):
        pass
    def write(self, text):      
        text = text.rstrip()
        stdout.write('%s %s\n' % (datetime.now().strftime('%H:%M:%S'), text))
        self.log.write('%s %s\n' % (datetime.now().strftime('%H:%M:%S'), text))
        return
