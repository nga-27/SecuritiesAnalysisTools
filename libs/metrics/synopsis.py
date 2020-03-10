def generate_synopsis(analysis: dict, **kwargs) -> dict:

    name = kwargs.get('name')
    print_out = kwargs.get('print_out', False)

    synopsis = dict()
    if name is None:
        return synopsis

    for period in analysis[name]:
        synopsis[period] = {'tabular': {}, 'metrics': {}}

        if (period != 'metadata') and (period != 'synopsis'):
            if print_out:
                print("")
                print(f"Time period: {period}")
                print("")

            for metric in analysis[name][period]:
                if metric != 'name':
                    mets = analysis[name][period][metric].get('metrics')
                    if mets is not None:
                        if isinstance(mets, (dict)):
                            for met in mets:
                                met_str = f"{metric} ({met})"
                                synopsis[period]['metrics'][met_str] = mets[met][-1]
                                if print_out:
                                    tabs = strings_to_tabs(met_str)
                                    print(
                                        f"metrics: {met_str} {tabs} {mets[met][-1]}")
                        else:
                            met_str = f"{metric}"
                            synopsis[period]['metrics'][met_str] = mets[-1]
                            if print_out:
                                tabs = strings_to_tabs(met_str)
                                print(f"metrics: {met_str} {tabs} {mets[-1]}")

                    mets = analysis[name][period][metric].get('tabular')
                    if mets is not None:
                        if isinstance(mets, (dict)):
                            for met in mets:
                                met_str = f"{metric} ({met})"
                                synopsis[period]['tabular'][met_str] = mets[met][-1]
                                if print_out:
                                    tabs = strings_to_tabs(met_str)
                                    print(
                                        f"tabular: {met_str} {tabs} {mets[met][-1]}")
                        else:
                            met_str = f"{metric}"
                            synopsis[period]['tabular'][met_str] = mets[-1]
                            if print_out:
                                tabs = strings_to_tabs(met_str)
                                print(f"tabular: {met_str} {tabs} {mets[-1]}")

    return synopsis


def strings_to_tabs(string: str) -> str:
    if len(string) < 4:
        tabs = '\t\t\t\t'
    elif len(string) < 7:
        tabs = '\t\t\t\t'
    elif len(string) < 12:
        tabs = '\t\t\t'
    elif len(string) < 15:
        tabs = '\t\t\t'
    elif len(string) < 22:
        tabs = '\t\t'
    else:
        tabs = '\t'

    return tabs
