import pandas as pd 
import numpy as np 
import json 
import os


def metadata_copy(data: dict) -> dict:
    """ Speciality copy function to remove tabulars, etc. """
    meta = data.copy()
    for key in meta.keys():
        meta[key].pop('clustered_osc')
        if 'features' in meta[key].keys():
            for feature in meta[key]['features']:
                for feat in range(len(meta[key]['features'][feature]['features'])):
                    # Array of 'feature' features
                    meta[key]['features'][feature]['features'][feat].pop('indexes')

    return meta


def output_to_json(data: dict, exclude_tabular=True):
    """ Simple function that outputs dictionary to JSON file """
    filename = 'output/metadata.json'
    if not os.path.exists('output/'):
        os.mkdir('output')
    if os.path.exists(filename):
        os.remove(filename)

    meta = metadata_copy(data)

    with open(filename, 'w') as f:
        json.dump(meta, f)

    print('JSON output complete.')
