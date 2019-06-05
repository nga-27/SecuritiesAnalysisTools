# SecuritiesAnalysisTools
Technical analysis tools for securities (funds, stocks, bonds, equities).

## Versioning
* 0.1.0, 2019-06-04 - Release 1: outputing to pptx and json files; basic analysis; primarily plot based

## To Use
1. Run `pip install -r requirements.txt`
1. Run the top-level job file.  For example, `technical_analysis.py`
1. Run `python technical_analysis.py` or `python release_1.py`
1. Answer input prompt of stock ticker (default is 'VTI', hitting simply 'enter')

## Acknowledgements
* [ranaroussi](https://pypi.org/project/fix-yahoo-finance/) for `PyPI fix-yahoo-finance`
* J. Arthur for python-pptx library
* B. Henry, V. Chevrier for great discussion and theories on market behavior, technical analysis

## Miscellaneous
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
