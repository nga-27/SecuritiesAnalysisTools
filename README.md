# SecuritiesAnalysisTools
Technical analysis tools for securities (funds, stocks, bonds, equities).

## Notable Versioning / Releases
* 0.1.0, 2019-06-04 - Release 1: outputing to pptx and json files; basic analysis; primarily plot based
* 0.1.06, 2019-07-13 - Wide 16:9 ratio for pptx output
* 0.1.11, 2019-08-13 - Upgraded requirements, some better documentation, and mutual fund timeframe issue resolved
* 0.1.x - Working toward Release 2 (`technical_analysis.py` is always current on master)

## To Use
1. Pull repository, start local, virtual, and/or global python environment.
1. Run `pip install -r requirements.txt`.  (Validate modules installed from _Other Library Installations_ section.)
1. Save file `core_example.json` as `core.json`. Edit new file as desired. This is recommended but not required.
1. Run the top-level job file.  For most updated functionality, run `python technical_analysis.py`.
1. After intro screen in terminal, an input prompt with 3 options (all followed by "enter" / "return"):
    * Default: 'VTI' and 'S&P500' by simply hitting "enter" / "return"
    * Input tickers: any string of tickers (space-delimited) can be entered. Example: `mmm AAPL 'AMZN'`
    * "Core": starting version 0.1.02+, entering `--core` when prompted for tickers will run `core.json` funds
        * Functionality offers an update on a user's porfolio w/o requiring entering it in all of the time
1. All default behavior (non-core) is `1 year period, 1 day interval`. (View `yfinance` api for other settings).


## Acknowledgements
* [ranaroussi](https://pypi.org/project/fix-yahoo-finance/) for `PyPI yfinance` (formerly `fix-yahoo-finance`)
* M. Olberding for countless algorithm postulations, great programming discourse, contributions to this endeavor
* J. Arthur for python-pptx library
* B. Henry, V. Chevrier, J. Arthur for great discussion and theories on market behavior, technical analysis

## Miscellaneous
### "Core" Functionality
Adding `core.json` file to your repo (see 'To Use' above) can allow the user to look at any number of tickers without having to 
manually add them in to the input prompt every single time. Simply enter in `--core` when prompted to input ticker symbols and the
software will read the `core.json` file. If the file does not exist, it will run the default behavior (as if simply clicking 'enter').

Core functionality provides the user to build up a list of investments he or she owns and/or typically monitors. `core.json` is part of
gitignore, so privacy of one's funds will be maintained.

### "Core" Properties
* **Period** - timeframe of historical stock data. Default is 1 year. (Provides 'Open', 'Close', 'High', 'Low', 'Volume', and 'Adj Close' for each fund.)
* **Interval** - data point frequency of historical stock data. Default is 1 day.
* **Indexes** - various 'Composite' metrics that give an overall health (in terms of oscillators) of a sector or asset type. The higher the index value, the more
"signifcant" the **SELL** signal; the lower the index value, the more "signifcant" the **BUY** signal.
    * `Market Composite` - summation of 'Clustered Oscillator' metrics for 11 sectors of stock market based off Vanguard's sector ETFs:
        * VHT (Healthcare), VGT (InfoTech), VNQ (Realestate), VIS (Industrial), VDE (Energy/Oil), VCR (ConsumerDiscretionary), VDC (ConsumerStaples)
        * VPU (Utilities), VAW (RawMaterials), VOX (Telcomm), and VFH (Financials)
    * `Corporate Bond` - summation of 'Clustered Oscillator' metrics for 3 corporate bond timeframes based off Vanguard's corp bond ETFs:
        * VCSH (Short-term), VCIT (Intermediate-term), and VCLT (Long-term)
    * `Treasury Bond` - summation of 'Clustered Oscillator' metrics for 4 investment-grade, treasury/gov't-based bonds and timeframes based off select Vanguard ETFs:
        * VGSH (Short-term), VGIT (Intermediate-Term), VGLT (Long-Term), and VTEB (tax-exempt municipal)
    * `International Composite` - weighted summation of 'Clustered Oscilator' metrics for 2 select Vanguard international ETFs:
        * BNDX (International Index), VWO (Emerging Markets Index)

FUTURE - adding more customizable fields to core functionality for greater user costumization.

## Python Libraries / Issues
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
