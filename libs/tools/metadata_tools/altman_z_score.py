""" Altman Z Score Derivation """

GOOD_THRESHOLD = 3.0
BAD_THRESHOLD = 1.8

def get_altman_z_score(meta: dict) -> dict:
    """Get Altman Z-Score

    Created by Prof. Edward Altman (1968), info here:
    https://www.investopedia.com/terms/a/altman.asp

    Each "letter" or term (A-E) represents a different aspect of a company's balance sheet:
        A: Liquidity
        B: Accumulated profits vs. assets
        C: How much profits the assets are producing
        D: Company's value vs. its liabilities
        E: Efficiency ratio (how much sales are generated from assets)

    Arguments:
        meta {dict} -- metadata object

    Returns:
        dict -- altman_z_score object
    """
    # pylint: disable=too-many-locals,too-many-return-statements,too-many-branches
    balance_sheet = meta.get('balance_sheet')
    financials = meta.get('financials')
    info = meta.get('info')

    if balance_sheet is None or financials is None or info is None:
        return {"score": "n/a", "values": {}}

    total_assets = balance_sheet.get("Total Assets")
    if total_assets is None:
        return {"score": "n/a", "values": {}}

    # Use this if yahoo hasn't updated their stats immediately following an earnings report
    used_total_assets = None
    for tot_assets in total_assets:
        if tot_assets and str(tot_assets) != "nan":
            used_total_assets = tot_assets
            break

    if not used_total_assets:
        return {"score": "n/a", "values": {}}

    current_assets = balance_sheet.get("Current Assets")
    if current_assets is None:
        return {"score": "n/a", "values": {}}

    current_liabilities = balance_sheet.get("Current Liabilities")
    if current_liabilities is None:
        return {"score": "n/a", "values": {}}

    working_capital = current_assets[0] / current_liabilities[0]
    altman_a = working_capital / used_total_assets * 1.2

    retained_earnings = balance_sheet.get("Retained Earnings")
    if retained_earnings is None:
        return {"score": "n/a", "values": {}}

    # Use this if yahoo hasn't updated their stats immediately following an earnings report
    used_retained_earnings = None
    for ret_earn in retained_earnings:
        if ret_earn and str(ret_earn) != "nan":
            used_retained_earnings = ret_earn
            break

    if not used_retained_earnings:
        return {"score": "n/a", "values": {}}

    altman_b = 1.4 * (used_retained_earnings / used_total_assets)

    e_bit = financials.get("EBIT")
    if e_bit is None:
        return {"score": "n/a", "values": {}}

    altman_c = 3.3 * (e_bit[0] / used_total_assets)

    market_cap = info.get("marketCap")
    if market_cap is None:
        return {"score": "n/a", "values": {}}

    total_liabilities = balance_sheet.get("Current Liabilities")
    if total_liabilities is None:
        return {"score": "n/a", "values": {}}
    altman_d = 0.6 * market_cap / total_liabilities[0]

    total_revenue = financials.get("Total Revenue")
    if total_revenue is None:
        return {"score": "n/a", "values": {}}

    altman_e = total_revenue[0] / used_total_assets
    altman = altman_a + altman_b + altman_c + altman_d + altman_e

    if altman >= GOOD_THRESHOLD:
        color = "green"
    elif altman > BAD_THRESHOLD:
        color = "yellow"
    else:
        color = "red"

    z_score = {
        "score": altman,
        "color": color,
        "values":
        {
            "A": altman_a,
            "B": altman_b,
            "C": altman_c,
            "D": altman_d,
            "E": altman_e
        }
    }

    return z_score
