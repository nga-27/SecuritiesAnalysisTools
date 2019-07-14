# SecuritiesAnalysisTools
Technical analysis tools for securities (funds, stocks, bonds, equities).

## Notable Versioning / Releases
* 0.1.0, 2019-06-04 - Release 1: outputing to pptx and json files; basic analysis; primarily plot based
* 0.1.06, 2019-07-13 - Wide 16:9 ratio for pptx output
* 0.1.x - Working toward Release 2 (`technical_analysis.py` is always current on master)

## To Use
1. Run `pip install -r requirements.txt`
1. Save file `core_example.json` as `core.json`. Edit new file as desired.
1. Run the top-level job file.  For DEV functionality, `technical_analysis.py`. Run `release_1.py` for PROD.
1. Answer input prompt of stock ticker (default is 'VTI', hitting simply 'enter'). 
    * With version 0.1.02+, entering in `--core` when prompted for tickers will run `core.json` funds.

## Acknowledgements
* [ranaroussi](https://pypi.org/project/fix-yahoo-finance/) for `PyPI fix-yahoo-finance`
* J. Arthur for python-pptx library
* B. Henry, V. Chevrier for great discussion and theories on market behavior, technical analysis

## Miscellaneous
### core.json Functionality
Adding `core.json` file to your repo (see 'To Use' above) can allow the user to look at any number of tickers without having to 
manually add them in to the input prompt every single time. Simply enter in `--core` when prompted to input ticker symbols and the
software will read the `core.json` file. If the file does not exist, it will run the default behavior (as if simply clicking 'enter').

Core functionality provides the user to build up a list of investments he or she owns and/or typically monitors. `core.json` is part of
gitignore, so privacy of one's funds will be maintained.

FUTURE - adding more customizable fields to core functionality for greater user costumization.

### Other Library Installations 
Run `pip install yfinance --upgrade --no-cache-dir` (note: 'upgrade' and 'no-cache...' might be omitted)
Run `pip install python-pptx`

### Matplotlib & OSX errors
If matplotlib.backend has issues with OSX, try running `conda install matplotlib` to solve issue.
If that does not solve issue, see [StackOverFlow Solution](https://stackoverflow.com/questions/21784641/installation-issue-with-matplotlib-python) for other ways of solving issue.

### Notable links:
[Yahoo Finance Python](https://pypi.org/project/fix-yahoo-finance/)

[Top 4 Tech Tools](https://www.investopedia.com/articles/active-trading/041814/four-most-commonlyused-indicators-trend-trading.asp)

[Tip Ranks, Metadata](https://www.tipranks.com/)

## Custom Metrics 
* _Clustered Oscillators_ - weighted-aggregate of RSI, Stochastic, and Ultimate Oscillators. **Higher: sell, lower: buy**
* _Market Composite Index_ - equal weight aggregate of all 11 market sectors of clustered oscillators
* _Swing Trades_ - logic to find trends using exponential moving averages. **Higher: sell, lower: buy**
