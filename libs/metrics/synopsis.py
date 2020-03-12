import numpy as np

from libs.utils import SP500


def generate_synopsis(analysis: dict, **kwargs) -> dict:

    name = kwargs.get('name')
    print_out = kwargs.get('print_out', False)

    synopsis = dict()
    if name is None:
        return synopsis

    for period in analysis[name]:
        synopsis[period] = {'tabular': {}, 'metrics': {}}

        if (period != 'metadata') and (period != 'synopsis'):

            for metric in analysis[name][period]:
                if (metric != 'name'):
                    mets = analysis[name][period][metric].get('metrics')
                    if mets is not None:
                        if isinstance(mets, (dict)):
                            for met in mets:
                                met_str = f"{metric} ({met})"
                                synopsis[period]['metrics'][met_str] = mets[met][-1]
                        else:
                            met_str = f"{metric}"
                            if met_str == 'trendlines':
                                synopsis[period]['metrics'][met_str] = mets
                            else:
                                synopsis[period]['metrics'][met_str] = mets[-1]

                    mets = analysis[name][period][metric].get('tabular')
                    if mets is not None:
                        if isinstance(mets, (dict)):
                            for met in mets:
                                met_str = f"{metric} ({met})"
                                synopsis[period]['tabular'][met_str] = mets[met][-1]
                        else:
                            met_str = f"{metric}"
                            synopsis[period]['tabular'][met_str] = mets[-1]

    output_to_terminal(synopsis, print_out=print_out, name=name)

    return synopsis


def strings_to_tabs(string: str) -> str:
    if len(string) < 4:
        tabs = '\t\t\t\t\t'
    elif len(string) < 7:
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

                print(f"Tabular:\r\n")
                for tab in synopsis[period]['tabular']:
                    tabs = strings_to_tabs(tab)
                    if isinstance(synopsis[period]['tabular'][tab], (str)):
                        print(
                            f"{tab} {tabs} {synopsis[period]['tabular'][tab]}")
                    else:
                        print(
                            f"{tab} {tabs} {np.round(synopsis[period]['tabular'][tab], 5)}")

                print(f"\r\nMetrics:\r\n")
                for met in synopsis[period]['metrics']:
                    tabs = strings_to_tabs(met)
                    if isinstance(synopsis[period]['metrics'][met], (str, list)):
                        print(
                            f"{met} {tabs} {synopsis[period]['metrics'][met]}")
                    else:
                        print(
                            f"{met} {tabs} {np.round(synopsis[period]['metrics'][met], 5)}")
