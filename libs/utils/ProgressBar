"""
ProgressBar utility class
"""

class ProgressBar(object):

    def __init__(self, total_items: int, name: str=''):
        self.total = total_items
        self.name = name + ' Progress'
        self.iteration = 0


    def start(self):
        self.printProgressBar(self.iteration, self.total, prefix=self.name)


    def update(self, iteration: int):
        self.printProgressBar(iteration, self.total, prefix=self.name)


    def uptick(self):
        self.iteration += 1
        self.printProgressBar(self.iteration, self.total, prefix=self.name)


    # Print iterations progress - courtesy of Greenstick (stackoverflow: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console)
    def printProgressBar (self, iteration, total, prefix='Progress', suffix='Complete', decimals = 1, length = 50, fill = '█'):
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
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
        # Print New Line on Complete
        if iteration == total: 
            print()
