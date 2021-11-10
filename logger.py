# This made by vietng322611, please be respect, don't copy it without permission, you can change the code inside into your code.

from datetime import datetime
import sys

class logger:
    config = {}
    def __init__(self, f):
        self.file = f
        self.stdout = sys.stdout
        self.log = open(self.file["Log_Path"] + 'log-' + str(datetime.now().date()) + '.txt', 'a')
    def flush(self):
        pass
    def write(self, text):      
        text = text.rstrip()
        self.stdout.write('%s %s\n' % (datetime.now().strftime('%H:%M:%S'), text))
        self.log.write('%s %s\n' % (datetime.now().strftime('%H:%M:%S'), text))
        return
