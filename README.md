# SecuritiesAnalysisTools
Technical analysis tools for securities (funds, stocks, bonds, equities).

## Notable Versioning / Releases
* 0.1.0, 2019-06-04 - Release 1: outputing to pptx and json files; basic analysis; primarily plot based
* 0.1.06, 2019-07-13 - Wide 16:9 ratio for pptx output
* 0.1.11, 2019-08-13 - Upgraded requirements, some better documentation, and mutual fund timeframe issue resolved
* 0.1.13, 2019-08-18 - Architecture overhaul (now `app.py`), terminal input options, error handling, robust backward compatibility to release 1
* 0.1.16, 2019-08-23 - Data download / formatting overhaul (a `dict()` of `pd.DataFrames`); fixes `NaN` fields
* 0.1.19, 2019-11-10 - Dataset exportation to csv, expanded `functions` capability
* 0.1.x - Working toward Release 2 (`app.py` with no `--rX` tags [X = available release] is most current on master)

## To Use
1. Pull repository, start local, virtual, and/or global python environment.
1. Run `pip install -r requirements.txt`.  (Validate modules installed from _Other Library Installations_ section.)
1. Save file `core_example.json` as `core.json`. Edit new file as desired. This is recommended but not required.
    * Optional (0.1.16+) a save the `test_example.json` as `test.json` as an optional supplement to `core.json
1. Run `python app.py`
1. After intro screen in terminal, an input prompt with 4+ options (all followed by "enter" / "return"):
    * Default: 'VTI' and 'S&P500' by simply hitting "enter" / "return"
    * Input tickers: any string of tickers (space-delimited) can be entered. Example: `mmm AAPL 'AMZN'`
    * "Core": starting version 0.1.02, entering `--core` when prompted for tickers will run `core.json` user funds and settings.
        * Functionality offers an update on a user's porfolio w/o requiring entering it in all of the time
    * "Test": starting version 0.1.16, entering `--test` when prompted for tickers will run `test.json` user funds and settings.
        * Functionality is the same as "core", but provides another means of configurability, especially for development.
    * "Options": starting version 0.1.13, entering `--options` will halt operation and print available input tags. (see _"Options"_ below)
1. All default behavior (non-core) is `2 year period, 1 day interval`. (View `yfinance` api for other settings).


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

New with 0.1.16, an optional `test.json` file can be added with the same functionality and concept as `--core`. For usage, simply enter
`--test`.  This can be helpful when branching this repo and testing things separate from one's main `core.json` list. This is entirely 
optional.

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

FUTURE - adding more customizable fields to core functionality for greater user customization.

### "Core" Exports
* **Run** - as expected, `True` if exportation to be run and `False` if to be omitted. (Can be run separately on prompt of `--export-dataset`.)
* **Fields** - optional specific fields to be exported to .csv. `fields` must be single string of keys: (e.g. `"fields": "rsi vpu macd vti"`)
    * Fields inputs should be matched to ticker symbols and  `ACCEPTED_ATTS`, listed below (2019-11-10)
        * `['statistics', 'macd', 'rsi', 'relative_strength', 'mci', 'correlation', 'futures']`
        * fields are not case-sensitive (though `--export-dataset` input key _IS_ case-sensitive)
    * If ticker symbols and/or `ACCEPTED_ATTS` are left `" "` while `run = True`, then default behavior is to run all available tabular dataset of all available tickers.

### "Options" at Input
Starting with **0.1.13**, the input prompt handles varying inputs beyond simply `--core`. All of the available (and some future) options are available at the
starting prompt by entering `--options`. This input will print out in the terminal available options from `resources/header_options.txt`. (Please, do not update this
file as it is read only into the program.) The program will also complete after printing out the available option keys. Please run the program again with the desired
-- tags.

## Python Libraries / Issues
Software is designed and run on **Python 3.6+**.

### Other Library Installations 
Run `pip install yfinance --upgrade --no-cache-dir` (note: 'upgrade' and 'no-cache...' might be omitted)

Run `pip install python-pptx`

### Matplotlib & OSX errors
If matplotlib.backend has issues with OSX, try running `conda install matplotlib` to solve issue.

If that does not solve issue, see [StackOverFlow Solution](https://stackoverflow.com/questions/21784641/installation-issue-with-matplotlib-python) for other ways of solving issue.
Other solutions, employed on all plotting functions, is the `register_matplotlib_converters()` function call preceding all plotting code at the beginning of each function.

### Notable links:
[Yahoo Finance Python](https://pypi.org/project/fix-yahoo-finance/)

[Top 4 Tech Tools](https://www.investopedia.com/articles/active-trading/041814/four-most-commonlyused-indicators-trend-trading.asp)

[Tip Ranks, Metadata](https://www.tipranks.com/)

## Custom Metrics 
* _Clustered Oscillators_ - weighted-aggregate of RSI, Stochastic, and Ultimate Oscillators. **Higher: sell, lower: buy**
* _Market Composite Index_ - equal weight aggregate of all 11 market sectors of clustered oscillators
* _Swing Trades_ - logic to find trends using exponential moving averages. **Higher: sell, lower: buy**
