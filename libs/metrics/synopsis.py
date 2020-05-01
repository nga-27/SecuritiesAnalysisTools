import numpy as np

from libs.utils import SP500, TEXT_COLOR_MAP, EXEMPT_METRICS

DOWN = TEXT_COLOR_MAP.get('red')
UP = TEXT_COLOR_MAP.get('green')
NORMAL = TEXT_COLOR_MAP.get('white')


def generate_synopsis(analysis: dict, **kwargs) -> dict:
    """Generate Synopsis

    Arguments:
        analysis {dict} -- fund & time period data object

    Optional Args:
        name {str} -- (default: {None})
        print_output {bool} -- print to terminal (default: {False})

    Returns:
        dict -- summarized keys for a "dashboard"
    """
    name = kwargs.get('name')
    print_out = kwargs.get('print_out', False)

    synopsis = dict()
    if name is None:
        return synopsis

    for period in analysis[name]:

        if period not in EXEMPT_METRICS:
            synopsis[period] = {
                'tabular': {},
                'metrics': {},
                'tabular_delta': {},
                'metrics_delta': {},
                'tabular_categories': {},
                'metrics_categories': {}
            }

            for metric in analysis[name][period]:
                if (metric != 'name'):
                    mets = analysis[name][period][metric].get('metrics')
                    cat = analysis[name][period][metric].get('type')

                    if mets is not None:
                        if isinstance(mets, (dict)):
                            for met in mets:
                                met_str = f"{metric} ({met})"
                                synopsis[period]['metrics'][met_str] = mets[met][-1]
                                cat = analysis[name][period][metric].get(
                                    'type')

                                if cat is not None:
                                    if (cat == 'trend') and (('metrics' in met_str) or
                                                             ('swing' in met_str)):
                                        cat = 'oscillator'
                                    if cat not in synopsis[period]['metrics_categories']:
                                        synopsis[period]['metrics_categories'][cat] = [
                                        ]
                                    synopsis[period]['metrics_categories'][cat].append(
                                        met_str)

                                diff = mets[met][-2]
                                synopsis[period]['metrics_delta'][met_str] = np.round(
                                    diff, 3)

                        else:
                            met_str = f"{metric}"
                            cat = analysis[name][period][metric].get('type')
                            if met_str == 'trendlines':
                                synopsis[period]['metrics'][met_str] = mets
                                synopsis[period]['metrics_delta'][met_str] = ''
                            else:
                                if cat is not None:
                                    if (cat == 'trend') and (('metrics' in met_str) or
                                                             ('swing' in met_str)):
                                        cat = 'oscillator'
                                    if cat not in synopsis[period]['metrics_categories']:
                                        synopsis[period]['metrics_categories'][cat] = [
                                        ]
                                    synopsis[period]['metrics_categories'][cat].append(
                                        met_str)

                                synopsis[period]['metrics'][met_str] = mets[-1]
                                diff = mets[-2]
                                synopsis[period]['metrics_delta'][met_str] = np.round(
                                    diff, 3)

                    mets = analysis[name][period][metric].get('tabular')
                    cat = analysis[name][period][metric].get('type')
                    if mets is not None:
                        if isinstance(mets, (dict)):
                            for met in mets:
                                met_str = f"{metric} ({met})"
                                synopsis[period]['tabular'][met_str] = mets[met][-1]
                                cat = analysis[name][period][metric].get(
                                    'type')

                                if cat is not None:
                                    if (cat == 'trend') and (('metrics' in met_str) or
                                                             ('swing' in met_str)):
                                        cat = 'oscillator'

                                    if cat not in synopsis[period]['tabular_categories']:
                                        synopsis[period]['tabular_categories'][cat] = [
                                        ]
                                    synopsis[period]['tabular_categories'][cat].append(
                                        met_str)

                                if isinstance(mets[met][-1], (str, list)):
                                    synopsis[period]['tabular_delta'][met_str] = ''

                                else:
                                    diff = mets[met][-2]
                                    synopsis[period]['tabular_delta'][met_str] = np.round(
                                        diff, 3)
                        else:
                            met_str = f"{metric}"
                            synopsis[period]['tabular'][met_str] = mets[-1]

                            if cat is not None:
                                if (cat == 'trend') and (('metrics' in met_str) or
                                                         ('swing' in met_str)):
                                    cat = 'oscillator'
                                if cat not in synopsis[period]['tabular_categories']:
                                    synopsis[period]['tabular_categories'][cat] = []
                                synopsis[period]['tabular_categories'][cat].append(
                                    met_str)

                            if isinstance(mets[-1], (str, list)):
                                synopsis[period]['tabular_delta'][met_str] = ''
                            else:
                                diff = mets[-2]
                                synopsis[period]['tabular_delta'][met_str] = np.round(
                                    diff, 3)

    output_to_terminal(synopsis, print_out=print_out, name=name)

    return synopsis


def strings_to_tabs(string: str, style='default') -> str:
    """Strings to Tabs

    Applies a number of tabs to best create a fake column in terminal

    Arguments:
        string {str} -- string to tab

    Keyword Argument:
        style {str} -- type of printout, 'default' or 'percent' (default: {'default'})

    Returns:
        str -- properly formatted string
    """
    if style == 'default':
        if len(string) < 7:
            tabs = '\t\t\t\t\t'
        elif len(string) < 12:
            tabs = '\t\t\t\t'
        elif len(string) < 15:
            tabs = '\t\t\t\t'
        elif len(string) < 23:
            tabs = '\t\t\t'
        elif len(string) < 30:
            tabs = '\t\t'
        else:
            tabs = '\t'

    elif style == 'percent':
        if len(string) < 7:
            tabs = '\t\t\t'
        elif len(string) < 12:
            tabs = '\t\t'
        elif len(string) < 15:
            tabs = '\t\t'
        elif len(string) < 23:
            tabs = '\t'
        elif len(string) < 30:
            tabs = ''
        else:
            tabs = ''

    else:
        return ''

    return tabs


def output_to_terminal(synopsis: dict, print_out=False, **kwargs):
    """Output to Terminal

    Mapping function to show fund information in terminal

    Arguments:
        synopsis {dict} -- synopsis object to output

    Keyword Arguments:
        print_out {bool} -- (default: {False})

    Optional Args:
        name {str} -- (default: {''})
    """
    name = kwargs.get('name', '')
    name2 = SP500.get(name, name)
    if print_out:
        for period in synopsis:

            if (period != 'metadata') and (period != 'synopsis'):
                print("\r\n")
                print(f"Time period: {period} for {name2}")
                print("")

                tabs = strings_to_tabs("Tabular:")
                tabs2 = strings_to_tabs("Current", style='percent')
                print(f"\r\nTabular:{tabs} Current{tabs2}Previous\r\n")

                for tab in synopsis[period]['tabular']:
                    custom_print(tab, synopsis[period]['tabular'][tab],
                                 prev=synopsis[period]['tabular_delta'][tab],
                                 thr=synopsis[period]['tabular_delta'][tab])

                tabs = strings_to_tabs("Metrics:")
                tabs2 = strings_to_tabs("Current", style='percent')
                print(f"\r\n\r\nMetrics:{tabs} Current{tabs2}Previous\r\n")

                for met in synopsis[period]['metrics']:
                    custom_print(met, synopsis[period]['metrics'][met],
                                 prev=synopsis[period]['metrics_delta'][met])


def custom_print(key: str, value, prev=None, thr=0.0):
    """Custom Print

    Specific printer for terminals; line by line primarily

    Arguments:
        key {str} -- synopsis key
        value {[type]} -- whichever value of the key

    Keyword Arguments:
        prev {[type]} -- previous value, if desired to be printed (default: {None})
        thr {float} -- value threshold for colors (default: {0.0})
    """
    tabs = strings_to_tabs(key)
    if isinstance(value, (str, list)):
        print(
            f"{key} {tabs} {value}")
    else:
        value = np.round(value, 5)
        tabs2 = strings_to_tabs(str(value), style='percent')
        color = NORMAL
        if value > thr:
            color = UP
        elif value < thr:
            color = DOWN
        print(
            f"{key} {tabs} {color}{value}{NORMAL}{tabs2}{prev}")
