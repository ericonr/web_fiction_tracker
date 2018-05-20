#this one attempts to not use ncurses
#source: https://stackoverflow.com/a/21008062/9512804

import sys
from time import sleep

class ProgressBar:
    def __init__(self, full, length, title='', show_percentage=False, show_elements=False):
        self.full = full
        self.length = length
        if title != '':
            self.title = title
        self.show_percentage = show_percentage
        self.show_elements = show_elements
        self.progress_x = 0

    def start(self):
        self.string = self.title + ": [" + "-" * self.length + "]"
        self.add_extras(0)
        sys.stdout.write(self.string)
        sys.stdout.flush()

    def update(self, element):
        x = (element * self.length) // self.full
        self.string = "#" * x + "-" * (self.length - x) + "]"
        self.add_extras(element)
        sys.stdout.write(self.string)
        sys.stdout.flush()
        self.progress_x = x

    def end(self):
        self.string = "#" * self.length + "]"
        self.add_extras(self.full)
        self.string += "\n"
        sys.stdout.write(self.string)
        sys.stdout.flush()

    def add_extras(self, element):
        new = ''
        if self.show_percentage:
            new += '[{}%]'.format((element * 100) // self.full)
        if self.show_elements:
            new += '[{}/{}]'.format(element, self.full)
        self.string += new + chr(8) * (self.length + 1 + len(new))
        return len(new)

def startprogress(title):
    """Creates a progress bar 40 chars long on the console
    and moves cursor back to beginning with BS character"""
    global progress_x
    sys.stdout.write(title + ": [" + "-" * 40 + "]" + chr(8) * 41)
    sys.stdout.flush()
    progress_x = 0


def progress(x):
    """Sets progress bar to a certain percentage x.
    Progress is given as whole percentage, i.e. 50% done
    is given by x = 50"""
    global progress_x
    x = int(x * 40 // 100)                      
    sys.stdout.write("#" * x + "-" * (40 - x) + "]" + chr(8) * 41)
    sys.stdout.flush()
    progress_x = x


def endprogress():
    """End of progress bar;
    Write full bar, then move to next line"""
    sys.stdout.write("#" * 40 + "]\n")
    sys.stdout.flush()

if __name__ == '__main__':
    startprogress('Test')
    for i in range(100):
        progress(i)
        sleep(.01)
    endprogress()

    bar = ProgressBar(100, 50, 'Test', True, True)
    bar.start()
    for i in range(100):
        bar.update(i)
        sleep(.01)
    bar.end()
