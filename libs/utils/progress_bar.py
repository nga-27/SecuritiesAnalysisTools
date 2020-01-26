"""
ProgressBar utility class
"""
from .constants import TEXT_COLOR_MAP, STANDARD_COLORS

BAR_COLOR = TEXT_COLOR_MAP["white"]
NORMAL = STANDARD_COLORS["normal"]
FUND_COLOR = TEXT_COLOR_MAP["cyan"]


class ProgressBar(object):

    def __init__(self, total_items: int, name: str = ''):
        self.total = float(total_items)
        self.name = name
        self.iteration = 0.0
        self.length_of_bar = 0
        self.has_finished = False

    def start(self):
        self.printProgressBar(self.iteration, self.total, obj=self.name)

    def update(self, iteration: int):
        self.printProgressBar(iteration, self.total, obj=self.name)

    def end(self):
        self.printProgressBar(self.total, self.total, obj=self.name)

    def uptick(self, increment=1.0):
        self.iteration += increment
        self.printProgressBar(self.iteration, self.total, obj=self.name)

    def interrupt(self, message: str = ''):
        clearBar = ''
        for _ in range(self.length_of_bar):
            clearBar += ' '
        clearBar += '\r'
        print(clearBar)
        print(message)

    # Print iterations progress - courtesy of Greenstick (stackoverflow: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console)

    def printProgressBar(self, iteration, total, obj='', prefix='Progress', suffix='Complete', decimals=1, length=50, fill='█'):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100.0 *
                                                         (float(iteration) / float(total)))
        filledLength = int(float(length) * float(iteration) // float(total))
        bar = fill * filledLength + '.' * (length - filledLength)

        pBar = f"\r {FUND_COLOR}{obj}{NORMAL} {prefix} {BAR_COLOR}|{bar}|{NORMAL} {percent}% {suffix}"
        self.length_of_bar = len(pBar)

        print(pBar, end='\r')

        # Print New Line on Complete
        if iteration == total:
            print('')
