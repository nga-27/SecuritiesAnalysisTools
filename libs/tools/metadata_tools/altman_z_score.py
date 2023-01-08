

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
    GOOD_THRESHOLD = 3.0
    BAD_THRESHOLD = 1.8

    balance_sheet = meta.get('balance_sheet')
    financials = meta.get('financials')
    info = meta.get('info')
    if balance_sheet is None or financials is None or info is None:
        return {"score": "n/a", "values": {}}

    total_assets = balance_sheet.get("Total Assets")
    if total_assets is None:
        return {"score": "n/a", "values": {}}

    current_assets = balance_sheet.get("Current Assets")
    if current_assets is None:
        return {"score": "n/a", "values": {}}

    current_liabilities = balance_sheet.get("Current Liabilities")
    if current_liabilities is None:
        return {"score": "n/a", "values": {}}

    working_capital = current_assets[0] / current_liabilities[0]
    altman_a = working_capital / total_assets[0] * 1.2

    retained_earnings = balance_sheet.get("Retained Earnings")
    if retained_earnings is None:
        return {"score": "n/a", "values": {}}

    altman_b = 1.4 * (retained_earnings[0] / total_assets[0])

    e_bit = financials.get("EBIT")
    if e_bit is None:
        return {"score": "n/a", "values": {}}

    altman_c = 3.3 * (e_bit[0] / total_assets[0])

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

    altman_e = total_revenue[0] / total_assets[0]
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
