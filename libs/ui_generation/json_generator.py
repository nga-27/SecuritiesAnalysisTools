"""
json_generator.py

Outputs a json file with entire 'analysis' data. Currently, file is relatively unused
in saved form. Can be used later with more complex ML or analytical tools.
"""

import json
import os


def metadata_copy(data: dict) -> dict:
    """Metadata Copy

    Specialty copy function to remove tabulars, etc. Pops selected tabular keys/data

    Arguments:
        data {dict} -- data object

    Returns:
        dict - copied metadata
    """
    meta = data.copy()
    for key in meta:
        if 'clustered_osc' in meta[key]:
            meta[key].pop('clustered_osc')
            #  Additional grooming / popping follows

    return meta


def output_to_json(data: dict, config: dict, exclude_tabular: bool = True):
    """Output to JSON

    Simple function that outputs dictionary to JSON file

    Arguments:
        data {dict} -- metadata to output to json file

    Keyword Arguments:
        exclude_tabular {bool} -- pop tabular data if True (default: {True})
    """
    filename = os.path.join("output", "metadata.json")
    if not os.path.exists('output'):
        os.mkdir('output')
    if os.path.exists(filename):
        os.remove(filename)

    meta = data
    if exclude_tabular:
        meta = metadata_copy(data)

    if 'debug' in config.get('state', ''):
        # This is to test serialization of keys
        for fund_name in meta:
            for key in meta[fund_name]:
                print(f"JSON testing {fund_name}: {key}")
                with open(f'output/temp/__{fund_name}_{key}.json', 'w', encoding='utf-8') as dump_f:
                    json.dump(meta, dump_f)

    with open(filename, 'w', encoding='utf-8') as dump_f:
        json.dump(meta, dump_f)

    print('\r\nJSON output complete.')
