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
from releases.prod import technical_analysis as prod
from releases.dev import technical_analysis as dev
from libs.utils import start_header, TEXT_COLOR_MAP, logo_renderer

################################
_VERSION_ = '0.1.28'
_DATE_REVISION_ = '2020-03-20'
################################


class App:

    NORMAL_COLOR = TEXT_COLOR_MAP["white"]
    PROD_COLOR = TEXT_COLOR_MAP["green"]

    def __init__(self):
        self.config = dict()
        self.isEnabled = True

    def run(self):
        logo_renderer()
        self.config = start_header(
            update_release=_DATE_REVISION_, version=_VERSION_, options=True)

        if 'run' in self.config['state']:
            self.config['release'] = False
            print(
                f"{self.PROD_COLOR}~~~~ PRODUCTION ENVIRONMENT ~~~~{self.NORMAL_COLOR}")
            print(" ")
            prod(self.config)

        if 'dev' in self.config['state']:
            self.config['release'] = True
            dev(self.config)

        print('Done.')


app = App()

if __name__ == '__main__':
    app.run()
