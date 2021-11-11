# This made by vietng322611, please respect, do not copy without permission, you can change the code inside to your own.

from datetime import datetime
from sys import stdout

class logger:
    config = {}
    def __init__(self, f):
        self.file = f
        self.log = open(self.file["Log_Path"] + 'log-' + str(datetime.now().date()) + '.txt', 'a')
        self.log.write('---------------------------------------------')
    def flush(self):
        pass
    def write(self, text):      
        text = text.rstrip()
        if text != '':
           stdout.write('%s\n' % (text))
           self.log.write('%s\n' % (text))
        return