import numpy as np

from libs.utils import SP500, TEXT_COLOR_MAP

DOWN = TEXT_COLOR_MAP.get('red')
UP = TEXT_COLOR_MAP.get('green')
NORMAL = TEXT_COLOR_MAP.get('white')


def generate_synopsis(analysis: dict, **kwargs) -> dict:

    name = kwargs.get('name')
    print_out = kwargs.get('print_out', False)

    synopsis = dict()
    if name is None:
        return synopsis

    for period in analysis[name]:
        synopsis[period] = {'tabular': {}, 'metrics': {},
                            'tabular_delta': {}, 'metrics_delta': {}}

        if (period != 'metadata') and (period != 'synopsis'):

            for metric in analysis[name][period]:
                if (metric != 'name'):
                    mets = analysis[name][period][metric].get('metrics')
                    if mets is not None:
                        if isinstance(mets, (dict)):
                            for met in mets:
                                met_str = f"{metric} ({met})"
                                synopsis[period]['metrics'][met_str] = mets[met][-1]
                                diff = mets[met][-2]
                                # diff = ((mets[met][-1] + 1.1) - (mets[met][-2] + 1.1)) / \
                                # (mets[met][-2] + 1.1) * 100.0
                                synopsis[period]['metrics_delta'][met_str] = np.round(
                                    diff, 3)
                        else:
                            met_str = f"{metric}"
                            if met_str == 'trendlines':
                                synopsis[period]['metrics'][met_str] = mets
                                synopsis[period]['metrics_delta'][met_str] = ''
                            else:
                                synopsis[period]['metrics'][met_str] = mets[-1]
                                # if mets[-2] == 0.0:
                                #     diff = (mets[-1] - 2.0) / 2.0 * 100.0
                                # else:
                                #     diff = (mets[-1] - mets[-2]) / \
                                #         np.abs(mets[-2]) * 100.0
                                diff = mets[-2]
                                synopsis[period]['metrics_delta'][met_str] = np.round(
                                    diff, 3)

                    mets = analysis[name][period][metric].get('tabular')
                    if mets is not None:
                        if isinstance(mets, (dict)):
                            for met in mets:
                                met_str = f"{metric} ({met})"
                                synopsis[period]['tabular'][met_str] = mets[met][-1]
                                if isinstance(mets[met][-1], (str, list)):
                                    synopsis[period]['tabular_delta'][met_str] = ''
                                else:
                                    # diff = ((mets[met][-1] + 1.1) - (mets[met][-2] + 1.1)) / \
                                    #     (mets[met][-2] + 1.1) * 100.0
                                    diff = mets[met][-2]
                                    synopsis[period]['tabular_delta'][met_str] = np.round(
                                        diff, 3)
                        else:
                            met_str = f"{metric}"
                            synopsis[period]['tabular'][met_str] = mets[-1]
                            if isinstance(mets[-1], (str, list)):
                                synopsis[period]['tabular_delta'][met_str] = ''
                            else:
                                # diff = ((mets[-1] + 1.1) - (mets[-2] + 1.1)) / \
                                #     (mets[-2] + 1.1) * 100.0
                                diff = mets[-2]
                                synopsis[period]['tabular_delta'][met_str] = np.round(
                                    diff, 3)

    output_to_terminal(synopsis, print_out=print_out, name=name)

    return synopsis


def strings_to_tabs(string: str, style='default') -> str:
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
