from datetime import datetime
import sys

class logger():
    def __init__(self, f):
        self.config = f
        self.stdout = sys.stdout
        self.log = open(self.config["Log_Path"] + 'log-' + str(datetime.now().date()) + '.txt', 'a')
    def flush(self):
        pass
    def write(self, text):      
        text = text.rstrip()
        self.stdout.write('%s %s\n' % (datetime.now().strftime('%H:%M:%S'), text))
        self.log.write('%s %s\n' % (datetime.now().strftime('%H:%M:%S'), text))
        return