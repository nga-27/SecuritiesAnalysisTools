import pandas as pd 
import numpy as np 


def has_critical_error(item, e_type: str, misc: dict=None) -> bool:
    """ Generic Error checker of items """
    
    if e_type == 'download_data':
        # A successful pull of actual data will have multiIndex keys. A single bad ticker will have columns but no data.
        if 'Close' not in item.keys():
            for fund in item.keys():
                # Check each ticker to validate data
                if len(fund) > 1:
                    if pd.isna(item[fund[0]]['Close'][1]):
                        print(f"404 ERROR: Data requested of ticker '{fund[0]}' not found. Input traceback: {misc} provided")
                        return True
            return False

        if len(item['Close']) == 0:
            print(f"404 ERROR: Data requested not found. Input traceback: {misc} provided")
            return True

    return False