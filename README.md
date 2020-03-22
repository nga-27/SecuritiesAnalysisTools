# SecuritiesAnalysisTools
Technical analysis tools for securities (funds, stocks, bonds, equities).

## Notable Versioning / Releases
* **0.1.0, 2019-06-04** - Release 1: outputing to pptx and json files; basic analysis; primarily plot based
* 0.1.06, 2019-07-13 - Wide 16:9 ratio for pptx output
* 0.1.11, 2019-08-13 - Upgraded requirements, some better documentation, and mutual fund timeframe issue resolved
* 0.1.13, 2019-08-18 - Architecture overhaul (now `app.py`), terminal input options, error handling, robust backward compatibility to release 1
* 0.1.16, 2019-08-23 - Data download / formatting overhaul (a `dict()` of `pd.DataFrames`); fixes `NaN` fields
* 0.1.19, 2019-11-10 - Dataset exportation to csv, expanded `functions` capability
* 0.1.21, 2019-12-01 - API expansion, metadata from yfinance
* 0.1.25, 2020-02-08 - Start of a normalized metric across all items (oscillators covered here)
* 0.1.27, 2020-03-09 - Multi-period data analysis ('10y', '5y', '2y', '1y'; '1d', '1w', '1m')
* 0.1.28, 2020-03-20 - PDF export of metrics, numerical details
* **0.2.0, 2020-03-22** - Release 2: Reorganization of `dev` and `prod` as functions, stable base

## To Use
1. Pull repository, start local, virtual, and/or global python environment.
1. Run `pip install -r requirements.txt`.  (Validate modules installed from _Other Library Installations_ section.)
1. Save file `core_example.json` as `core.json`. Edit new file as desired. This is recommended but not required.
    * Optional (0.1.16+) a save the `test_example.json` as `test.json` as an optional supplement to `core.json
1. Run `python app.py`
1. After intro screen in terminal, an input prompt with 5+ options (all followed by "enter" / "return"):
    * Default: 'VTI' and 'S&P500' by simply hitting "enter" / "return"
    * Input tickers: any string of tickers (space-delimited) can be entered. Example: `mmm AAPL 'AMZN'`
    * "Core": starting version 0.1.02, entering `--core` when prompted for tickers will run `core.json` user funds and settings.
        * Functionality offers an update on a user's porfolio w/o requiring entering it in all of the time
    * "Test": starting version 0.1.16, entering `--test` when prompted for tickers will run `test.json` user funds and settings.
        * Functionality is the same as "core", but provides another means of configurability, especially for development.
    * "Options": starting version 0.1.13, entering `--options` will halt operation and print available input tags. (see _"Options"_ below)
    * "Functions": starting version 0.1.17, entering `--f` will allow a *function* to be run without the main service. (see *"Functions"* below)
1. All default behavior (non-core) is `2 year period, 1 day interval`. (View `yfinance` api for other settings).


## Acknowledgements
* [ranaroussi](https://github.com/ranaroussi/yfinance) for `PyPI yfinance` (formerly `fix-yahoo-finance`)
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
* **Period** - timeframe of historical stock data. Default is 2 years. (Provides 'Open', 'Close', 'High', 'Low', 'Volume', and 'Adj Close' for each fund.) Options include: 1 year, 2 years, 5 years, and 10 years.
* **Interval** - data point frequency of historical stock data. Default is 1 day. Options include: 1 day, 1 week, and 1 month.
* **Indexes** - various 'Composite' metrics that give an overall health (in terms of oscillators) of a sector or asset type. The lower the index value, the more "signifcant" the **SELL** signal; the higher the index value, the more "signifcant" the **BUY** signal.
    * `Market Composite` - summation of 'Clustered Oscillator' metrics for 11 sectors of stock market based off Vanguard's sector ETFs:
        * VHT (Healthcare), VGT (InfoTech), VNQ (Realestate), VIS (Industrial), VDE (Energy/Oil), VCR (ConsumerDiscretionary), VDC (ConsumerStaples)
        * VPU (Utilities), VAW (RawMaterials), VOX (Telcomm), and VFH (Financials)
    * `Corporate Bond` - summation of 'Clustered Oscillator' metrics for 3 corporate bond timeframes based off Vanguard's corp bond ETFs:
        * VCSH (Short-term), VCIT (Intermediate-term), and VCLT (Long-term)
    * `Treasury Bond` - summation of 'Clustered Oscillator' metrics for 4 investment-grade, treasury/gov't-based bonds and timeframes based off select Vanguard ETFs:
        * VGSH (Short-term), VGIT (Intermediate-Term), VGLT (Long-Term), and VTEB (tax-exempt municipal)
    * `International Composite` - weighted summation of 'Clustered Oscillator' metrics for 2 select Vanguard international ETFs:
        * BNDX (International Index), VWO (Emerging Markets Index)
    * `Type Composite` - grouped summation of 'Clustered Oscillator' metrics for 11 sectors grouped into the following categories:
        * Sensitive (Beta ~ 1.0, sensitive to market changes) - VGT, VOX, VIS, 50% of VDE, and 50% of VHT
        * Defensive (Beta < 1.0, slower growth but less volatile) - VDC, VPU, 50% of VHT, and 60% of VNQ
        * Cyclical (Beta > 1.0, has normal economic cycles) - VCR, VFH, VAW, 50% of VDE, and 40% of VNQ

### "Core" Exports
* **Run** - as expected, `True` if exportation to be run and `False` if to be omitted. (Can be run separately on prompt of `--export-dataset`.)
* **Fields** - optional specific fields to be exported to .csv. `fields` must be single string of keys: (e.g. `"fields": "rsi vpu macd vti"`)
    * Fields inputs should be matched to ticker symbols and  `ACCEPTED_ATTS`, listed below (2020-03-01)
        * `['statistics', 'macd', 'rsi', 'relative_strength', 'mci', 'correlation', 'futures', 'moving_average', 'swing_trade', 'obv', 'awesome', 'momentum_oscillator', 'bear_bull_power', 'total_power', 'hull_moving_average']`
        * fields are not case-sensitive (though `--export` input key _IS_ case-sensitive)
    * If ticker symbols and/or `ACCEPTED_ATTS` are left `" "` while `run = True`, then default behavior is to run all available tabular dataset of all available tickers.

### "Options" at Input
Starting with **0.1.13**, the input prompt handles varying inputs beyond simply `--core`. All of the available (and some future) options are available at the starting prompt by entering `--options`. This input will print out in the terminal available options from `resources/header_options.txt`. (Please, do not update this file as it is read only into the program.) The program will also complete after printing out the available option keys. Please run the program again with the desired `--` tags.

### "Functions" at Input
Starting with **0.1.17**, the input prompt can provide a subset of technical analysis tools to the user without having to run the entire main program and generate outputs. This subset of tools are run through the *"functions"* flag, denoted by `--f`. An advantage of this is if a user wishes to see, perhaps, only RSI and Exponential Moving Average (EMA) for securities *MMM* and *VTI*, only those will be run. Any function can be added with no limit to the number of functions added (see list of functions by running `--options`). Similarly, any number of tickers can be added with the configurable *period* and *interval* flags as well.

An example input to generate an output of an RSI, EMA, and Hull Moving Average for a 5 year window at 1 week intervals for AAPL, MMM, and VWINX would be:

`--f --rsi --ema --hull --5y --1w aapl mmm vwinx`

All plots created during the process are rendered in real time. Note: **nothing is saved in "functions" mode**. To have saved plots or data, one must run the full program and `--export`.  Any function added without the `--f` flag will not be registered as a function and could give undesired behavior.

## Python Libraries / Issues
Software is designed and run on **Python 3.6+**.

### Other Library Installations 
Run `pip install yfinance --upgrade --no-cache-dir` (note: 'upgrade' and 'no-cache...' might be omitted)

Run `pip install python-pptx`

### Matplotlib & OSX errors
If matplotlib.backend has issues with OSX, try running `conda install matplotlib` to solve issue.

If that does not solve issue, see [StackOverFlow Solution](https://stackoverflow.com/questions/21784641/installation-issue-with-matplotlib-python) for other ways of solving issue.
Other solutions, employed on all plotting functions, is the `register_matplotlib_converters()` function call preceding all plotting code at the beginning of each function.

Note: this issue may have been resolved with `matplotlib 3.0.2`. As of v0.2.0, this software requires `matplotlib>=3.2.0`.

### Notable links:
[Yahoo Finance Python](https://pypi.org/project/yfinance/)

[Top 4 Tech Tools](https://www.investopedia.com/articles/active-trading/041814/four-most-commonlyused-indicators-trend-trading.asp)

[Tip Ranks, Metadata](https://www.tipranks.com/)

[TradingView - Awesome Charts](https://www.tradingview.com/)

## Custom Metrics 
* _Clustered Oscillators_ - weighted-aggregate of RSI, Stochastic, and Ultimate Oscillators. **Higher: buy, lower: sell**
* _Swing Trades_ - logic to create an oscillator signal using various moving averages. **Higher: buy, lower: sell**
* _Market Composite Index (MCI)_ - equal weight aggregate of all 11 market sectors of clustered oscillators
* _"X" Bond Composite Index (BCI)_ - similar to MCI except where *"X"* is *Treasury*, *Corporate*, or *International*. All three supported.
* _Correlation Composite Index (CCI)_ - mapping of various lookback periods of correlations of 11 sectors with S&P500.
* _Type Composite Index (TCI)_ - weighted indexes representing *Sensitive*, *Defensive*, and *Cyclical* stock sectors
