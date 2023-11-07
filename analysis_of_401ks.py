"""
Ruth vs. Dale

Both Ruth and Dale start working in industry at age 23 on Jan 1. They retire at 65.

Ruth is shrewd right out of uni, and she starts investing $12K / year in her 401K. She does this for
10 years. After that, she stops contributing.

Dale, for various reasons, does not contribute to his 401K until after his 10th year working. He
continues to contribute $12K to it every year until retirement.

Here are a few scenarios of payments and ending 401K amounts:

* Basic Ruth vs. Dale: at which age Dale will over take Ruth in more 401K? (Assume steady 5% growth)
* Basic Ruth vs. Dale Part 2: same as above, but what if Ruth never stops contributing?
* Semi-Stochastic market gains, weighted to 62% wins and 38% losses. How does that affect growth?
"""
import math
from typing import Tuple
import random
import numpy as np
import matplotlib.pyplot as plt

BASE_GROWTH = 0.05
OTHER_GROWTH = 0.06 # Since 1950, 8% has been the mean return of the S&P500
ANNUAL_CONTRIBUTION = 12000.0
START_AGE = 23.0
RMD_AGE = 73
TRADITIONAL_MIX = (0.0, 1.0)
ROTH_MIX = (1.0, 0.0)


def basic_ruth_vs_dale_adjusted(avg_return: float):
    # index 0 is end of first year of working, so end of 23 years old, for math purposes. Each year
    # will be 12 indexes, as we will be looking at months (0.05/12)
    ruth2 = [0.0]
    dale2 = [0.0]
    crossover = START_AGE
    age = [START_AGE]
    for i in range(12 * 42):
        if i < 120:
            ruth_new2 = ruth2[-1] * (1.0 + avg_return / 12.0) + (ANNUAL_CONTRIBUTION / 12.0)
            ruth2.append(ruth_new2)
            dale2.append(0.0)
        else:
            ruth_new2 = ruth2[-1] * (1.0 + avg_return / 12.0)
            ruth2.append(ruth_new2)
            dale_new2 = dale2[-1] * (1.0 + avg_return / 12.0) + (ANNUAL_CONTRIBUTION / 12.0)
            dale2.append(dale_new2)

        age.append(START_AGE + (float(i) / 12.0))
        if dale2[-1] > ruth2[-1] and crossover == START_AGE:
            crossover = round(age[-1], 1)

    if crossover == START_AGE:
        crossover = "NEVER"

    fig = plt.figure()
    plt.plot(age, ruth2)
    plt.plot(age, dale2)
    plt.legend([f'Ruth @ {avg_return*100.0}%', f'Dale @ {avg_return*100.0}%'])
    plt.ylabel('401K Value')
    plt.xlabel('Age')
    plt.title(f"Ruth vs. Dale {round(avg_return * 100, 3)}% Growth (Crossover at age {crossover})")
    plt.show()
    plt.close(fig)


def basic_ruth_vs_dale_without_stopping():
    # index 0 is end of first year of working, so end of 23 years old, for math purposes. Each year
    # will be 12 indexes, as we will be looking at months (0.05/12)
    ruth = [0.0]
    dale = [0.0]
    age = [START_AGE]
    crossover = START_AGE
    for i in range(12 * 42):
        ruth_new = ruth[-1] * (1.0 + BASE_GROWTH / 12.0) + (ANNUAL_CONTRIBUTION / 12.0)
        ruth.append(ruth_new)
        if i < 120:
            dale.append(0.0)
        else:
            dale_new = dale[-1] * (1.0 + BASE_GROWTH / 12.0) + (ANNUAL_CONTRIBUTION / 12.0)
            dale.append(dale_new)

        age.append(START_AGE + (float(i) / 12.0))
        if dale[-1] > ruth[-1] and crossover == START_AGE:
            crossover = round(age[-1], 1)

    fig = plt.figure()
    plt.plot(age, ruth)
    plt.plot(age, dale)
    plt.legend(['Ruth', 'Dale'])
    plt.ylabel('401K Value')
    plt.xlabel('Age')
    plt.title(f"Ruth vs. Dale (Ruth never stops)")
    plt.show()
    plt.close(fig)

def weighted_returns() -> float:
    # Need to scale the range gaussian.
    # https://towardsdatascience.com/are-stock-returns-normally-distributed-e0388d71267e
    # mu = 0.06, sigma=0.12
    MU = 0.06
    SIGMA = 0.12
    return random.gauss(MU, SIGMA)


def stochastic_basic():
    # index 0 is end of first year of working, so end of 23 years old, for math purposes. Each year
    # will be 12 indexes, as we will be looking at months (0.05/12)
    ruth = [0.0]
    dale = [0.0]
    age = [START_AGE]
    crossover = START_AGE
    for i in range(12 * 42):
        growth = weighted_returns()
        if i < 120:
            ruth_new = ruth[-1] * (1.0 + growth / 12.0) + (ANNUAL_CONTRIBUTION / 12.0)
            ruth.append(ruth_new)
            dale.append(0.0)
        else:
            ruth_new = ruth[-1] * (1.0 + growth / 12.0)
            ruth.append(ruth_new)
            dale_new = dale[-1] * (1.0 + growth / 12.0) + (ANNUAL_CONTRIBUTION / 12.0)
            dale.append(dale_new)

        age.append(START_AGE + (float(i) / 12.0))
        if dale[-1] > ruth[-1] and crossover == START_AGE:
            crossover = round(age[-1], 1)
    
    fig = plt.figure()
    plt.plot(age, ruth)
    plt.plot(age, dale)
    plt.legend(['Ruth', 'Dale'])
    plt.ylabel('401K Value')
    plt.xlabel('Age')
    plt.title(f"Ruth vs. Dale (Stochastic)")
    plt.show()
    plt.close(fig)


# basic_ruth_vs_dale_adjusted(0.04)
# basic_ruth_vs_dale_adjusted(0.05)
# basic_ruth_vs_dale_adjusted(0.06)
# basic_ruth_vs_dale_adjusted(0.0625)
# basic_ruth_vs_dale_adjusted(0.07)
# basic_ruth_vs_dale_adjusted(0.08)
# basic_ruth_vs_dale_without_stopping()
# stochastic_basic()

# https://www.capitalgroup.com/individual/service-and-support/retirement-distributions/irs-uniform-lifetime-table.html
RMD_LIFE_EXP = [
    27.4, 26.5, 25.5, 24.6, 23.7, 22.9, 22., 21.1, 20.2, 19.4, 18.5, 17.7, 16.8, 16., 15.2,
    14.4, 13.7, 12.9, 12.2, 11.5, 10.8, 10.1, 9.5, 8.9, 8.4, 7.8, 7.3, 6.8, 6.4
]

TAX_TABLE = [
    [
        (10275, 0.1),
        (41775, 0.12),
        (89075, 0.22),
        (170050, 0.24),
        (215950, 0.32),
        (539900, 0.35),
        (100000000, 0.37)
    ],
    [
        (11000, 0.1),
        (44725, 0.12),
        (95375, 0.22),
        (182100, 0.24),
        (231250, 0.32),
        (578125, 0.35),
        (100000000, 0.37)
    ]
]

def gap_withdrawal_calc(savings: float, nominal: int, year_of_retirement: int, nom_pct: float = 0.04, nom_infl_pct: float = 0.03) -> float:
    actual_pct = nom_pct * (1.0 + year_of_retirement * nom_infl_pct)
    nominal *= 1.0 + (nom_infl_pct * year_of_retirement)
    amount = max(savings * actual_pct, nominal)
    return amount

def get_tax_on_income(working_income_yrly: int, tax_year: int = 1) -> Tuple[float, float]:
    if working_income_yrly <= 0:
        return 0.0, 0
    total_tax = 0.0
    amount_already_taxed = 0
    for _, tax in enumerate(TAX_TABLE[tax_year]):
        thresh, rate = tax
        if working_income_yrly <= thresh:
            total_tax += (working_income_yrly - amount_already_taxed) * rate
            break
        total_tax += (thresh - amount_already_taxed) * rate
        amount_already_taxed = thresh

    effective_rate = round(round(total_tax, 2) / float(working_income_yrly) * 100.0, 2)
    return effective_rate, total_tax

def growth_curve(max_growth: float, min_growth: float, years: int) -> list:
    growth = []
    midpoint = years * 0.6
    adj_max = max_growth - min_growth
    for i in range(years):
        val = adj_max / (1.0 + math.exp((i - midpoint) / 5)) + min_growth
        growth.append(val)
    return growth

def get_income(years_worked: int, max_income: int) -> list:
    x = np.linspace(1, years_worked)
    income = np.log(x) / np.log(years_worked) * (max_income / 2) + (max_income / 2)
    return income

def get_rmd_and_withdrawal(withdraw, rmd_amount) -> Tuple[float, float]:
    """ withdrawal, deposit """
    if rmd_amount > withdraw:
        # We'll get cash back for our brokerage
        return rmd_amount, rmd_amount - withdraw
    return withdraw, 0.0


def calculate_401K(max_income: int, annual_contribution: int, growth_range: Tuple[float, float],
                   annual_withdrawal: int, years_worked: int = 43,
                   mix_ratio: Tuple[float, float] = (0.5, 0.5)):
    """ Returns: combined, brokerage, roth, traditional, missed_roth_gains, total_traditional_taxes """
    growth = growth_curve(growth_range[0], growth_range[1], years_worked)
    _ = get_income(years_worked, max_income)

    retirement_yr = []
    brokerage_yr = []
    roth_yr = []
    trad_yr = []
    missed_from_taxes = []
    tot_trad_taxes_yr = []

    trad = 0.0
    roth = 0.0
    brokerage = 0.0
    missed = 0.0
    tot_trad_taxes = 0.0
    for year in range(years_worked):
        roth_contrib = mix_ratio[0] * annual_contribution
        trad_contrib = mix_ratio[1] * annual_contribution
        _, tax = get_tax_on_income(roth_contrib)
        missed += tax

        trad += trad_contrib
        roth += roth_contrib
        trad *= 1.0 + growth[year]
        roth *= 1.0 + growth[year]
        missed *= 1.0 + growth[year]

        missed_from_taxes.append(missed)
        roth_yr.append(roth)
        trad_yr.append(trad)
        retirement_yr.append(trad + roth)
        brokerage_yr.append(brokerage)
        tot_trad_taxes_yr.append(0.0)

    # Entire Retirement w/o RMDs
    years_retired = 0
    gap_years = RMD_AGE - (years_worked + int(START_AGE))
    for year in range(gap_years):
        amount_needed = 0.0
        tax_needed = 0.0
        withdrawal = gap_withdrawal_calc(roth + trad, annual_withdrawal, years_retired)

        if roth <= 0.0 and trad <= 0.0:
            roth = 0.0
            trad = 0.0
            if brokerage < withdrawal:
                brokerage = 0.0
            else:
                brokerage -= withdrawal
                _, tax = get_tax_on_income(withdrawal)
                tot_trad_taxes += tax
                brokerage -= tax
                if brokerage <= 0.0:
                    brokerage = 0.0

        elif roth > 0.0 and trad <= 0.0:
            if roth < withdrawal:
                amount_needed = withdrawal - roth
                roth = 0.0
            else:
                roth -= withdrawal

        elif trad > 0.0 and roth <= 0.0:
            if trad < withdrawal:
                amount_needed = withdrawal - trad
                _, tax = get_tax_on_income(trad)
                tax_needed += tax
                tot_trad_taxes += tax
                trad = 0.0
                if brokerage < amount_needed:
                    brokerage = 0.0
                else:
                    brokerage -= amount_needed
                    _, tax = get_tax_on_income(amount_needed)
                    tax_needed += tax
                    tot_trad_taxes += tax
                    brokerage -= tax_needed
                    if brokerage <= 0.0:
                        brokerage = 0.0
            else:
                trad -= withdrawal
                _, tax = get_tax_on_income(withdrawal)
                if trad < tax:
                    tax_needed += tax - trad
                    trad = 0.0
                    brokerage -= tax_needed
                    if brokerage < tax_needed:
                        brokerage = 0.0
                else:
                    trad -= tax
                    tot_trad_taxes += tax
        
        else:
            roth_contrib = withdrawal * mix_ratio[0]
            trad_contrib = withdrawal * mix_ratio[1]
            _, tax = get_tax_on_income(trad_contrib)
            tot_trad_taxes += tax
            if trad < trad_contrib:
                amount_needed = trad_contrib - trad
                trad = 0.0
                if roth >= amount_needed:
                    roth -= amount_needed
                else:
                    if brokerage < amount_needed:
                        brokerage = 0.0
                    else:
                        brokerage -= amount_needed
                        brokerage -= tax
                        if brokerage <= 0.0:
                            brokerage = 0.0
            else:
                trad -= trad_contrib
                if trad < tax:
                    tax_needed = tax - trad
                    trad = 0.0
                    brokerage -= tax_needed
                    if brokerage < 0.0:
                        brokerage = 0.0
                else:
                    trad -= tax
            
            if roth < roth_contrib:
                amount_needed = roth_contrib - roth
                roth = 0.0
                if trad >= amount_needed:
                    trad -= amount_needed
                    _, tax = get_tax_on_income(amount_needed)
                    tot_trad_taxes += tax
                    if trad < tax:
                        tax_needed += tax - trad
                        trad = 0.0
                        brokerage -= tax_needed
                        if brokerage <= 0.0:
                            brokerage = 0.0
                    else:
                        trad -= tax
                if brokerage < amount_needed:
                    brokerage = 0.0
                else:
                    brokerage -= amount_needed
                    _, tax = get_tax_on_income(amount_needed)
                    brokerage -= tax
                    if brokerage < 0.0:
                        brokerage = 0.0
            else:
                roth -= roth_contrib
            tot_trad_taxes += tax

        roth *= 1.0 + growth[-1]
        trad *= 1.0 + growth[-1]
        brokerage *= 1.0 + growth[-1]

        roth_yr.append(roth)
        trad_yr.append(trad)
        retirement_yr.append(roth + trad)
        missed_from_taxes.append(missed)
        brokerage_yr.append(brokerage)
        tot_trad_taxes_yr.append(tot_trad_taxes)
        years_retired += 1

    for _, rmd in enumerate(RMD_LIFE_EXP):
        amount_needed = 0.0
        tax_needed = 0.0
        if roth <= 0.0 and trad <= 0.0:
            roth = 0.0
            trad = 0.0
            if brokerage <= 0.0:
                brokerage = 0.0
            else:
                withdraw_trad = gap_withdrawal_calc(roth + trad, annual_withdrawal, years_retired)
                _, tax = get_tax_on_income(withdraw_trad)
                tot_trad_taxes += tax
                brokerage -= withdraw_trad
                brokerage -= tax
                if brokerage < 0.0:
                    brokerage = 0.0
        
        elif trad <= 0.0 and roth > 0.0:
            withdraw_roth = gap_withdrawal_calc(roth + trad, annual_withdrawal, years_retired)
            if roth < withdraw_roth:
                amount_needed = withdraw_roth - roth
                roth = 0.0
                if brokerage < amount_needed:
                    brokerage = 0.0
                else:
                    brokerage -= amount_needed
                    _, tax = get_tax_on_income(amount_needed)
                    tot_trad_taxes += tax
                    brokerage -= tax
                    if brokerage < 0.0:
                        brokerage = 0.0
            else:
                roth -= withdraw_roth

        elif trad > 0.0 and roth <= 0.0:
            withdraw_trad = gap_withdrawal_calc(roth + trad, annual_withdrawal, years_retired)
            rmd_amt = trad * rmd / 100.0
            withdraw_trad, deposit = get_rmd_and_withdrawal(withdraw_trad, rmd_amt)
            if trad < withdraw_trad:
                amount_needed = withdraw_trad - trad
                _, tax = get_tax_on_income(trad)
                tot_trad_taxes += tax
                tax_needed += tax
                trad = 0.0
                if brokerage < amount_needed:
                    brokerage = 0.0
                else:
                    brokerage -= amount_needed
                    brokerage -= tax_needed
                    _, tax = get_tax_on_income(amount_needed)
                    tot_trad_taxes += tax
                    brokerage -= tax
                    if brokerage < 0.0:
                        brokerage = 0.0
            else:
                trad -= withdraw_trad
                brokerage += deposit
                _, tax = get_tax_on_income(withdraw_trad)
                tot_trad_taxes += tax
                if trad < tax:
                    tax_needed = tax - trad
                    trad = 0.0
                    if brokerage < tax_needed:
                        brokerage = 0.0
                    else:
                        brokerage -= tax_needed
                else:
                    trad -= tax

        else:
            withdrawal = gap_withdrawal_calc(roth + trad, annual_withdrawal, years_retired)
            rmd_amt = trad * rmd / 100.0
            withdraw_trad, deposit = get_rmd_and_withdrawal(withdrawal * mix_ratio[1], rmd_amt)
            withdraw_roth = withdrawal * mix_ratio[0]
            if trad < withdraw_trad:
                amount_needed += withdraw_trad - trad
                _, tax = get_tax_on_income(trad)
                tot_trad_taxes += tax
                tax_needed += tax
                trad = 0.0
            else:
                trad -= withdraw_trad
                _, tax = get_tax_on_income(withdraw_trad)
                tot_trad_taxes += tax
                if trad < tax:
                    tax_needed += tax - trad
                    trad = 0.0
                else:
                    trad -= tax


            if roth < withdraw_roth:
                amount_needed += withdraw_roth - roth
                roth = 0.0
            else:
                roth -= withdraw_roth

            if trad <= 0.0 and roth > 0.0:
                if amount_needed:
                    if roth < amount_needed:
                        amount_needed -= roth
                        roth = 0.0
                    else:
                        roth -= amount_needed
                        amount_needed = 0.0
                if tax_needed:
                    if roth < tax_needed:
                        tax_needed -= roth
                        roth = 0.0
                    else:
                        roth -= tax_needed
                        tax_needed = 0.0

            brokerage += deposit
            if brokerage < amount_needed:
                brokerage = 0.0
            else:
                brokerage -= amount_needed
                _, tax = get_tax_on_income(amount_needed)
                tot_trad_taxes += tax
                brokerage -= tax
            if brokerage < tax_needed:
                brokerage = 0.0
            else:
                brokerage -= tax_needed

        roth *= 1.0 + growth[-1]
        trad *= 1.0 + growth[-1]
        brokerage *= 1.0 + growth[-1]

        roth_yr.append(roth)
        trad_yr.append(trad)
        retirement_yr.append(roth + trad)
        brokerage_yr.append(brokerage)
        missed_from_taxes.append(missed)
        tot_trad_taxes_yr.append(tot_trad_taxes)
        years_retired += 1

    return retirement_yr, brokerage_yr, roth_yr, trad_yr, missed_from_taxes, tot_trad_taxes_yr

######################################################################



def experiment_with_rmds():
    _, broke, _, trad, _, total_tax = calculate_401K(200000, 13000, (0.08, 0.03), 36000, mix_ratio=TRADITIONAL_MIX)
    _, _, roth, _, missed, _ = calculate_401K(200000, 13000, (0.08, 0.03), 36000, mix_ratio=ROTH_MIX)
    fig = plt.figure()
    plt.plot(range(23, len(trad) + 23), trad)
    plt.plot(range(23, len(roth) + 23), roth)
    plt.plot(range(23, len(missed) + 23), missed)
    plt.plot(range(23, len(broke) + 23), broke)
    plt.plot(range(23, len(total_tax) + 23), total_tax)
    # plt.xscale('log')
    plt.ylabel('Value of 401K')
    plt.xlabel('Age')
    plt.legend(
        ['Traditional 401k', 'Roth 401k', 'Missed Gains from Roth Taxes', 'Taxable Brokerage', 'Total Traditional Tax'])
    plt.title(f"Tax Implications & RMDs on 401Ks")
    plt.show()
    plt.close(fig)

    combined = [t_val + broke[i] for i, t_val in enumerate(trad)]
    fig = plt.figure()
    plt.plot(range(23, len(combined) + 23), combined)
    plt.plot(range(23, len(roth) + 23), roth)
    # plt.xscale('log')
    plt.ylabel('Value of 401K')
    plt.xlabel('Age')
    plt.legend(
        ['Traditional 401k (with RMD Brokerage)', 'Roth 401k'])
    plt.title(f"Tax Implications & RMDs on 401Ks")
    plt.show()
    plt.close(fig)


def compare_traditionals():
    fig = plt.figure()
    _, broke, _, trad, _, _ = calculate_401K(60000, 2000, (0.08, 0.03), 25000, mix_ratio=TRADITIONAL_MIX)
    combined = [t_val + broke[i] for i, t_val in enumerate(trad)]
    plt.plot(range(23, len(combined) + 23), combined)
    _, broke, _, trad, _, _  = calculate_401K(60000, 3000, (0.08, 0.03), 25000, mix_ratio=TRADITIONAL_MIX)
    combined = [t_val + broke[i] for i, t_val in enumerate(trad)]
    plt.plot(range(23, len(combined) + 23), combined)
    _, broke, _, trad, _, _ = calculate_401K(60000, 4000, (0.08, 0.03), 25000, mix_ratio=TRADITIONAL_MIX)
    combined = [t_val + broke[i] for i, t_val in enumerate(trad)]
    plt.plot(range(23, len(combined) + 23), combined)
    plt.ylabel('Value of 401K')
    plt.xlabel('Age')
    plt.legend(
        ['$60K, $2K, $25K', '$60K, $3K, $25K', '$60K, $4K, $25K', '$100K, $4K, $25K', '$200K, $4K, $25K', 'rich only'])
    plt.title(f"Traditional 401K")
    plt.show()
    plt.close(fig)

def compare_roths():
    fig = plt.figure()
    roth, _, _, _, _, _ = calculate_401K(60000, 2000, (0.08, 0.03), 25000, mix_ratio=ROTH_MIX)
    plt.plot(range(23, len(roth) + 23), roth)
    roth, _, _, _, _, _ = calculate_401K(60000, 3000, (0.08, 0.03), 25000, mix_ratio=ROTH_MIX)
    plt.plot(range(23, len(roth) + 23), roth)
    roth, _, _, _, _, _ = calculate_401K(60000, 4000, (0.08, 0.03), 25000, mix_ratio=ROTH_MIX)
    plt.plot(range(23, len(roth) + 23), roth)
    plt.ylabel('Value of 401K')
    plt.xlabel('Age')
    plt.legend(
        ['$60K, $2K, $25K', '$60K, $3K, $25K', '$60K, $4K, $25K', '$100K, $4K, $25K', '$200K, $4K, $25K'])
    plt.title(f"Roth 401K Performance")
    plt.show()
    plt.close(fig)


def compare_mixed():
    fig = plt.figure()
    retire, broke, _, _, _, _ = calculate_401K(60000, 2000, (0.08, 0.03), 25000, mix_ratio=(0.5, 0.5))
    combined = [r_val + broke[i] for i, r_val in enumerate(retire)]
    plt.plot(range(23, len(combined) + 23), combined)
    retire, broke, _, _, _, _ = calculate_401K(60000, 3000, (0.08, 0.03), 25000, mix_ratio=(0.5, 0.5))
    combined = [r_val + broke[i] for i, r_val in enumerate(retire)]
    plt.plot(range(23, len(combined) + 23), combined)
    retire, broke, _, _, _, _ = calculate_401K(60000, 4000, (0.08, 0.03), 25000, mix_ratio=(0.5, 0.5))
    combined = [r_val + broke[i] for i, r_val in enumerate(retire)]
    plt.plot(range(23, len(combined) + 23), combined)
    plt.ylabel('Value of 401K')
    plt.xlabel('Age')
    plt.legend(
        ['$2K/yr', '$3K/yr', '$4K/yr'])
    plt.title(f"Mixed 401K Performance ($60000, $2K/yr)")
    plt.show()
    plt.close(fig)


def compare_all():
    fig = plt.figure()
    retire, broke, _, _, _, _ = calculate_401K(60000, 4000, (0.08, 0.03), 25000, mix_ratio=TRADITIONAL_MIX)
    combined = [r_val + broke[i] for i, r_val in enumerate(retire)]
    plt.plot(range(23, len(combined) + 23), combined)
    retire, _, _, _, _, _ = calculate_401K(60000, 4000, (0.08, 0.03), 25000, mix_ratio=ROTH_MIX)
    plt.plot(range(23, len(retire) + 23), retire)
    retire, broke, _, _, _, _ = calculate_401K(60000, 4000, (0.08, 0.03), 25000)
    combined = [r_val + broke[i] for i, r_val in enumerate(retire)]
    plt.plot(range(23, len(combined) + 23), combined)
    plt.ylabel('Value of 401K')
    plt.xlabel('Age')
    plt.legend(
        ['Traditional', 'Roth', 'Mixed 50-50'])
    plt.title(f"Comparison Plans at $60K, $4K/yr")
    plt.show()
    plt.close(fig)


def tax_rate_experiment():
    incomes = [5000, 10000, 15000, 20000, 30000, 50000, 75000, 100000, 150000, 200000, 300000, 400000,
            600000, 800000, 1000000, 2000000, 5000000, 10000000]

    tax_full = []
    for year in range(2):
        taxes = []
        for income in incomes:
            rate, _ = get_tax_on_income(income, year)
            taxes.append(rate)
        tax_full.append(taxes)

    fig = plt.figure()
    plt.plot(incomes, tax_full[0])
    plt.plot(incomes, tax_full[1])
    plt.xscale('log')
    plt.ylabel('Effective Tax Rate (%)')
    plt.xlabel('Annual Income ($)')
    plt.legend(['2022', '2023'])
    plt.title(f"Effective Tax Rate vs. Income")
    plt.show()
    plt.close(fig)

    fig = plt.figure()
    plt.plot(incomes, tax_full[0])
    plt.plot(incomes, tax_full[1])
    plt.ylabel('Effective Tax Rate (%)')
    plt.xlabel('Annual Income ($)')
    plt.legend(['2022', '2023'])
    plt.title(f"Effective Tax Rate vs. Income")
    plt.show()
    plt.close(fig)


def mixes_with_inputs():
    fig = plt.figure()
    legend = []
    for contrib in [500 + 500 * i for i in range(20)]:
        mixed, mix_broke, _, _, _, _ = calculate_401K(100000, contrib, (0.08, 0.03), 25000)
        combined = [mix + mix_broke[t] for t, mix in enumerate(mixed)]
        plt.plot(range(23, len(combined) + 23), combined)
        legend.append(f"${contrib}")
    plt.legend(legend)
    plt.title("Mixed 401K (50%) vs. Contribution at $100k Income")
    plt.show()
    plt.close(fig)

    fig = plt.figure()
    legend = []
    for income in [50000 + 10000 * i for i in range(20)]:
        mixed, mix_broke, _, _, _, _ = calculate_401K(income, 5000, (0.08, 0.03), 25000)
        combined = [mix + mix_broke[t] for t, mix in enumerate(mixed)]
        plt.plot(range(23, len(combined) + 23), combined)
        legend.append(f"${income}")
    plt.legend(legend)
    plt.title("Mixed 401k (50%) vs. Income at $5K Contribution")
    plt.show()
    plt.close(fig)


# Income contribution vs. Growth (same color for contribution amount, 3-8% growth range)
def mixes_with_inputs_and_growth():
    fig = plt.figure()
    legend = []
    plot_colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
    for contrib in [500 + 500 * z for z in range(20)]:
        mixed, mix_broke, _, _, _, _ = calculate_401K(100000, contrib, (0.08, 0.03), 25000)
        combined = [mix + mix_broke[t] for t, mix in enumerate(mixed)]
        plt.plot(range(23, len(combined) + 23), combined)
        legend.append(f"${contrib}")
    # plt.legend(legend)
    plt.title("Mixed 401K (50%): Contribution & Growth")
    plt.show()
    plt.close(fig)

    fig = plt.figure()
    legend = []
    plot_colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
    all_contribs = []
    all_eols = []
    for contrib in [500 + 500 * z for z in range(20)]:
        mixed, mix_broke, _, _, _, _ = calculate_401K(100000, contrib, (0.08, 0.03), 25000)
        combined = [mix + mix_broke[t] for t, mix in enumerate(mixed)]
        all_contribs.append(contrib)
        index = -1
        eol_val = 65
        while index > -1 * len(combined):
            if combined[index] > 0.0:
                eol_val = 101 + index
                break
            index -= 1
        all_eols.append(eol_val)
        plt.plot(all_contribs, all_eols)
        legend.append(f"Avg 401K Growth")
    plt.legend(legend)
    plt.title("Mixed 401K (50%): Contribution & Growth (Max 100 yrs)")
    plt.ylabel('Emptied 401k Age (Yrs)')
    plt.xlabel('Annual 401K Mixed Contribution ($)')
    plt.show()
    plt.close(fig)


def compare_mix_ratios(ranger: list = list(range(11))):
    fig = plt.figure()
    legend = []
    for roth in ranger:
        r_pct = roth / 10.0
        t_pct = 1.0 - r_pct
        legend.append(f"R{round(r_pct, 1)} / T{round(t_pct, 1)}")
        retire, broke, _, _, _, _ = calculate_401K(60000, 4000, (0.08, 0.03), 25000, mix_ratio=(r_pct, t_pct))
        combined = [r_val + broke[i] for i, r_val in enumerate(retire)]
        if roth == 10:
            plt.plot(range(23, len(combined) + 23), combined, color='black')
        else:
            plt.plot(range(23, len(combined) + 23), combined)
    plt.legend(legend)
    plt.title("Mixed 401K Ratios (Roth / Traditional)")
    plt.ylabel('Value of 401K')
    plt.xlabel('Age')
    plt.show()
    plt.close(fig)


def compare_contributions():
    fig = plt.figure()
    legend = []
    for i, contrib in enumerate([4000, 8000, 12000, 16000]):
        legend.extend([f"{contrib}-Mix", f"{contrib}-Trad", f"{contrib}-Roth"])
        withdraw = 25000 + i * 15000
        retire, broke, _, _, _, _ = calculate_401K(60000, contrib, (0.08, 0.03), withdraw, mix_ratio=(0.5, 0.5))
        retire_t, broke_t, _, _, _, _ = calculate_401K(60000, contrib, (0.08, 0.03), withdraw, mix_ratio=TRADITIONAL_MIX)
        retire_r, broke_r, _, _, _, _ = calculate_401K(60000, contrib, (0.08, 0.03), withdraw, mix_ratio=ROTH_MIX)
        combined = [r_val + broke[i] for i, r_val in enumerate(retire)]
        plt.plot(range(23, len(combined) + 23), combined)
        combined_t = [r_val + broke_t[i] for i, r_val in enumerate(retire_t)]
        plt.plot(range(23, len(combined_t) + 23), combined_t)
        combined_r = [r_val + broke_r[i] for i, r_val in enumerate(retire_r)]
        plt.plot(range(23, len(combined_r) + 23), combined_r)

    plt.legend(legend)
    plt.title("Mixed 401K Ratios (Roth / Traditional)")
    plt.ylabel('Value of 401K')
    plt.xlabel('Age')
    plt.show()
    plt.close(fig)


# tax_rate_experiment()
# experiment_with_rmds()
# compare_traditionals()
# compare_roths()
# compare_mixed()
# compare_all()
# compare_mix_ratios()
# compare_mix_ratios([0, 1, 10])
# mixes_with_inputs()
# mixes_with_inputs_and_growth()
compare_contributions()

# contribution vs. growth = line; line_f(contribution) vs. end of life; different lines of age (75, 80, 90, 100)
