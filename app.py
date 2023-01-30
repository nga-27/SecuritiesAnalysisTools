"""
#   Technical Analysis Tools
#
#   by: nga-27
#
#   A program that outputs a graphical and a numerical analysis of
#   securities (stocks, bonds, equities, and the like). Analysis
#   includes use of oscillators (Stochastic, RSI, and Ultimate),
#   momentum charting (Moving Average Convergence Divergence,
#   Simple and Exponential Moving Averages), trend analysis (Bands,
#   Support and Resistance, Channels), and some basic feature
#   detection (Head and Shoulders, Pennants).
#
"""
from libs.utils import start_header, logo_renderer
from releases.technical_analysis import technical_analysis, clock_management

################################
_VERSION_ = '1.0.00'
_DATE_REVISION_ = '2023-01-29'
################################


class App:
    """ Top Level Class Application """
    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.config = {}

    def run(self):
        """ Run function of Class and Application """
        logo_renderer()
        self.config = start_header(
            update_release=_DATE_REVISION_, version=_VERSION_, options=True)

        if 'run' in self.config['state']:
            self.config['release'] = False
            clock = technical_analysis(self.config)
            print(f"\r\nCompleted in {clock_management(clock)}.")

        print('Done.')


app = App()
if __name__ == '__main__':
    app.run()
