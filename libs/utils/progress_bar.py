"""
ProgressBar utility class
"""
import time
import numpy as np

from .constants import TEXT_COLOR_MAP, STANDARD_COLORS

BAR_COLOR = TEXT_COLOR_MAP["white"]
NORMAL = STANDARD_COLORS["normal"]
FUND_COLOR = TEXT_COLOR_MAP["cyan"]

EFFECTIVE_TIME_START = 120


class ProgressBar():
    """ProgressBar

    Useful class to track progress of a function or analysis set
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, total_items: int, name: str = '',
                 stopwatch: bool = True, offset: float = None):
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
        self.print_progress_bar(self.iteration, self.total, obj=self.name)

    def update(self, iteration: int):
        """ Manual changing of the progress bar """
        self.print_progress_bar(iteration, self.total, obj=self.name)

    def uptick(self, increment=1.0):
        """ Automatic updating of the progress bar """
        self.iteration += increment
        self.print_progress_bar(self.iteration, self.total, obj=self.name)

    def end(self) -> float:
        """ Sets all progress to 100% and returns time of completion """
        self.print_progress_bar(self.total, self.total, obj=self.name)
        return time.time()

    def interrupt(self, message: str = ''):
        """ Stops p-bar operation (not to 100%) and provides a message for stoppage """
        clear_bar = ''
        for _ in range(self.length_of_bar):
            clear_bar += ' '
        clear_bar += '\r'
        print(clear_bar)
        print(message)

    # Print iterations progress - courtesy of Greenstick (stackoverflow:
    # https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console)

    # pylint: disable=too-many-arguments
    def print_progress_bar(self,
                           iteration: int,
                           total: int,
                           obj: str = '',
                           prefix: str = 'Progress',
                           suffix: str = 'Complete',
                           decimals: int = 1,
                           length: int = 50,
                           fill: str = '█'):
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
        # pylint: disable=too-many-locals
        percent = ("{0:." + str(decimals) + "f}").format(100.0 *
                                                         (float(iteration) / float(total)))
        filled_length = int(float(length) * float(iteration) // float(total))
        bar_fill = fill * filled_length + '.' * (length - filled_length)

        p_bar = f"\r {FUND_COLOR}{obj}{NORMAL} {prefix} {BAR_COLOR}|{bar_fill}|{NORMAL} " + \
            f"{percent}% {suffix}"
        self.length_of_bar = len(p_bar)

        effective_length = len(f" {obj} {prefix} |{bar_fill}| {percent}% {suffix}")

        stopwatch = ""
        if self.show_clock:
            self.clock = np.round(
                time.time() - self.start_time, 0)

            num_spaces = EFFECTIVE_TIME_START - effective_length
            stopwatch = " " * num_spaces
            minutes = int(self.clock / 60)
            seconds = int(self.clock % 60)

            if minutes > 0:
                stopwatch += f"{minutes}m {seconds:02d}s"
            else:
                stopwatch += f"{self.clock}s"

        p_bar = f"\r {FUND_COLOR}{obj}{NORMAL} {prefix} {BAR_COLOR}|{bar_fill}|{NORMAL} " + \
            f"{percent}% {suffix}{stopwatch}"
        self.length_of_bar = len(p_bar)

        print(p_bar, end='\r')

        # Print New Line on Complete
        if iteration == total:
            print('')


def start_clock() -> float:
    """ Wrapper function for time keeping """
    return time.time()
