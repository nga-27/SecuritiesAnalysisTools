"""
ProgressBar utility class
"""
import time
import numpy as np

from .constants import TEXT_COLOR_MAP, STANDARD_COLORS

BAR_COLOR = TEXT_COLOR_MAP["white"]
NORMAL = STANDARD_COLORS["normal"]
FUND_COLOR = TEXT_COLOR_MAP["cyan"]


class ProgressBar(object):
    """ProgressBar

    Useful class to track progress of a function or analysis set

    Arguments:
        object {} -- n/a
    """

    def __init__(self, total_items: int, name: str = '', stopwatch: bool = True, offset=None):
        self.total = float(total_items)
        self.name = name
        self.iteration = 0.0
        self.length_of_bar = 0
        self.has_finished = False
        self.start_time = offset
        self.show_clock = stopwatch
        self.clock = self.start_time

    def start(self):
        """ Kicks off class timer, etc. """
        if self.start_time is None:
            self.start_time = time.time()
        self.printProgressBar(self.iteration, self.total, obj=self.name)

    def update(self, iteration: int):
        """ Manual changing of the progress bar """
        self.printProgressBar(iteration, self.total, obj=self.name)

    def uptick(self, increment=1.0):
        """ Automatic updating of the progress bar """
        self.iteration += increment
        self.printProgressBar(self.iteration, self.total, obj=self.name)

    def end(self):
        """ Sets all progress to 100% and returns time of completion """
        self.printProgressBar(self.total, self.total, obj=self.name)
        return time.time()

    def interrupt(self, message: str = ''):
        """ Stops p-bar operation (not to 100%) and provides a message for stoppage """
        clearBar = ''
        for _ in range(self.length_of_bar):
            clearBar += ' '
        clearBar += '\r'
        print(clearBar)
        print(message)

    # Print iterations progress - courtesy of Greenstick (stackoverflow:
    # https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console)

    def printProgressBar(self,
                         iteration,
                         total,
                         obj='',
                         prefix='Progress',
                         suffix='Complete',
                         decimals=1,
                         length=50,
                         fill='█'):
        """Print Progress Bar

        Call in a loop to create terminal progress bar

        Arguments:
            iteration {int} -- current iteration
            total {int} -- total iterations

        Keyword Arguments:
            prefix {str} -- prefix string (default: {'Progress'})
            suffix {str} -- suffix string (default: {'Complete'})
            decimals {int} positive number of decimals in percent complete (default: {1})
            length {int} -- character length of bar (default: {50})
            fill {str} -- bar fill character (default: {'█'})
        """
        percent = ("{0:." + str(decimals) + "f}").format(100.0 *
                                                         (float(iteration) / float(total)))
        filledLength = int(float(length) * float(iteration) // float(total))
        bar = fill * filledLength + '.' * (length - filledLength)

        pBar = f"\r {FUND_COLOR}{obj}{NORMAL} {prefix} {BAR_COLOR}|{bar}|{NORMAL} " + \
            f"{percent}% {suffix}"
        self.length_of_bar = len(pBar)

        stopwatch = ""
        if self.show_clock:
            self.clock = np.round(
                time.time() - self.start_time, 0)
            if self.length_of_bar < 149:
                stopwatch = f"\t{self.clock}s"
            if self.length_of_bar < 141:
                stopwatch = f"\t\t{self.clock}s"
            if self.length_of_bar < 133:
                stopwatch = f"\t\t\t{self.clock}s"
            if self.length_of_bar < 125:
                stopwatch = f"\t\t\t\t{self.clock}s"
            if self.length_of_bar < 117:
                stopwatch = f"\t\t\t\t\t{self.clock}s"

        pBar = f"\r {FUND_COLOR}{obj}{NORMAL} {prefix} {BAR_COLOR}|{bar}|{NORMAL} " + \
            f"{percent}% {suffix}{stopwatch}"
        self.length_of_bar = len(pBar)

        print(pBar, end='\r')

        # Print New Line on Complete
        if iteration == total:
            print('')


def start_clock():
    """ Wrapper function for time keeping """
    return time.time()
