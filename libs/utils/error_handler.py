import pandas as pd 
import numpy as np 
from .constants import TEXT_COLOR_MAP


error_color = TEXT_COLOR_MAP["yellow"]
note_color = TEXT_COLOR_MAP["white"]
normal_color = TEXT_COLOR_MAP["white"]

def has_critical_error(item, e_type: str, misc: dict=None) -> bool:
    """ Generic Error checker of items """
    
    if e_type == 'download_data':
        """ NaN errors here were handled with 0.1.16 for reformatting data and cleansing of NaN """

        for key in item.keys():
            if 'Close' not in item[key].keys():
                print(f"{error_color}WARNING DataException: Invalid dataset, contains no list 'Close' for '{key}'.")
                print(f"{note_color}Exiting...{normal_color}")
                return True 

            if len(item[key]['Close']) == 0:
                print(f"{error_color}WARNING DataException: Invalid dataset, has no listed data for 'Close' for '{key}'.")
                print(f"{note_color}Exiting...{normal_color}")
                return True
            
            # Assumption is that point or mutual fund NaN errors will be corrected in data.py before this error handler
            nans = list(np.where(pd.isna(item[key]['Close']) == True))[0]
            if len(nans) > 0:
                print("")
                print(f"{error_color}WARNING DataException: Invalid dataset, contains {len(nans)} NaN item(s) for 'Close' for '{key}'.")
                print(f"---> This error is likely caused by '{key}' being an invalid or deprecated ticker symbol.")
                print(f"{note_color}Exiting...{normal_color}")
                return True 

        return False

    return False