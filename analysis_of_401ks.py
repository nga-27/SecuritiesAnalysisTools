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
from typing import Tuple
import random
import numpy as np
import matplotlib.pyplot as plt

BASE_GROWTH = 0.05
OTHER_GROWTH = 0.06 # Since 1950, 8% has been the mean return of the S&P500
ANNUAL_CONTRIBUTION = 12000.0
START_AGE = 23.0


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
    14.4, 13.7, 12.9, 12.2, 11.5
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


def roth_vs_traditional_effective_rate(working_income_yrly: int, tax_year: int) -> Tuple[float, float]:
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


def roth_vs_traditional_meh(max_income: int, trad_pct: float, roth_pct: float, tax_year: int):
    MAX_YR_CAREER = 43
    x = np.linspace(1, MAX_YR_CAREER)
    income = np.log(x) / np.log(MAX_YR_CAREER) * (max_income / 2) + (max_income / 2)
    fig = plt.figure()
    plt.plot(x, income)
    plt.show()
    plt.close(fig)


def roth_vs_traditional(max_income: int, trad_amt: int, growth: float, gap_withdrawal: int):
    MAX_YR_CAREER = 43
    x = np.linspace(1, MAX_YR_CAREER)
    income = np.log(x) / np.log(MAX_YR_CAREER) * (max_income / 2) + (max_income / 2)

    traditional_401k = []
    roth_401k = []
    missed_out_from_taxes = []
    taxable_brokerage = []
    total_tax_traditional = []
    mixed = []
    mixed_brokerage = []

    invested_trad = 0.0
    invested_roth = 0.0
    missed_from_roth = 0.0
    invested_mix = 0.0
    for year in range(MAX_YR_CAREER):
        invested_trad += trad_amt
        invested_trad *= 1.0 + growth
        traditional_401k.append(invested_trad)

        _, tax_trad = roth_vs_traditional_effective_rate(income[year] - trad_amt, 1)
        _, tax_roth = roth_vs_traditional_effective_rate(income[year], 1)
        missed_from_roth += tax_roth - tax_trad
        missed_from_roth *= 1.0 + growth
        missed_out_from_taxes.append(missed_from_roth)

        invested_roth += trad_amt - (tax_roth - tax_trad)
        invested_roth *= 1.0 + growth
        roth_401k.append(invested_roth)

        invested_mix += trad_amt / 2.0
        invested_mix += trad_amt / 2.0 - (tax_roth - tax_trad) / 2.0
        invested_mix *= 1.0 + growth
        mixed.append(invested_mix)

    for _ in range(MAX_YR_CAREER):
        taxable_brokerage.append(0.0)
        mixed_brokerage.append(0.0)
        total_tax_traditional.append(0.0)

    total_tax_trad = 0.0
    for _ in range(7):
        # Same effective withdrawal (tax eats more gap_withdrawal)
        invested_trad -= gap_withdrawal
        _, tax_trad = roth_vs_traditional_effective_rate(gap_withdrawal, 1)
        invested_trad -= tax_trad
        invested_trad *= 1.0 + growth / 2.0
        traditional_401k.append(invested_trad)

        invested_roth -= gap_withdrawal
        invested_roth *= 1.0 + growth / 2.0
        roth_401k.append(invested_roth)

        total_tax_trad += tax_trad
        total_tax_traditional.append(total_tax_trad)
        
        invested_mix -= gap_withdrawal + (tax_trad / 2.0)
        invested_mix *= 1.0 + growth / 2.0
        mixed.append(invested_mix)

    for _ in range(7):
        missed_out_from_taxes.append(missed_from_roth)
        taxable_brokerage.append(0.0)
        mixed_brokerage.append(0.0)

    # RMD is taken from traditional (or 1.5 * withdrawal, whichever is max). This is removed from
    # the 401K. Anything more than 1.5 * withdrawal will go to Brokerage.
    brokerage = 0.0
    LONG_TERM_GAP = gap_withdrawal * 3 / 2
    LONG_TERM_GROWTH = 1.0 + growth / 2.0
    withdrawn = 0.0
    for _, rmd_year in enumerate(RMD_LIFE_EXP):
        amount_missing = 0.0
        if invested_trad <= 0.0:
            amount_missing = LONG_TERM_GAP
        else:
            if invested_trad <= LONG_TERM_GAP:
                withdrawn = invested_trad
                amount_missing = LONG_TERM_GAP - withdrawn
            else:
                rmd_amount = invested_trad * rmd_year / 100.0
                withdrawn = LONG_TERM_GAP
                if rmd_amount > LONG_TERM_GAP:
                    withdrawn = rmd_amount
                    # amount missing will be negative so as to add to brokerage
                    amount_missing = LONG_TERM_GAP - rmd_amount 
                
            invested_trad -= withdrawn
            _, tax = roth_vs_traditional_effective_rate(withdrawn, 1)
            invested_trad *= LONG_TERM_GROWTH
            total_tax_trad += tax
            brokerage -= tax

        if brokerage > 0.0:
            brokerage -= amount_missing
            if amount_missing > 0:
                _, tax = roth_vs_traditional_effective_rate(amount_missing, 1)
                total_tax_trad += tax
                brokerage -= tax
            brokerage *= LONG_TERM_GROWTH
            brokerage_ord_inc = brokerage * 0.7 * 0.03
            _, brokerage_inc_tax = roth_vs_traditional_effective_rate(brokerage_ord_inc, 1)
            brokerage += brokerage_ord_inc - brokerage_inc_tax
            total_tax_trad += brokerage_inc_tax

        if brokerage < 0.0:
            brokerage = 0.0

        traditional_401k.append(invested_trad)
        missed_out_from_taxes.append(missed_from_roth)
        taxable_brokerage.append(brokerage)
        total_tax_traditional.append(total_tax_trad)

    for _, rmd_year in enumerate(RMD_LIFE_EXP):
        invested_roth -= gap_withdrawal * 3 / 2
        invested_roth *= 1.0 + growth / 2.0
        if invested_roth <= 0.0:
            invested_roth = 0.0
        roth_401k.append(invested_roth)

    mix_broke = 0.0
    for _, rmd_year in enumerate(RMD_LIFE_EXP):
        rmd_used = False
        amount_missing = 0.0
        if invested_mix <= 0.0:
            amount_missing = LONG_TERM_GAP
        else:
            if invested_mix <= LONG_TERM_GAP:
                withdrawn = invested_mix
                amount_missing = LONG_TERM_GAP - invested_mix
            else:
                rmd_amount = invested_mix * rmd_year / 100.0 / 2.0
                withdrawn = LONG_TERM_GAP
                if rmd_amount > LONG_TERM_GAP:
                    withdrawn = rmd_amount
                    rmd_used = True
                    # amount missing will be negative so as to add to brokerage
                    amount_missing = LONG_TERM_GAP - rmd_amount
            
            invested_mix -= withdrawn
            _, tax = roth_vs_traditional_effective_rate(withdrawn / 2, 1)
            if rmd_used:
                _, tax = roth_vs_traditional_effective_rate(withdrawn, 1)
            invested_mix -= tax
            invested_mix *= LONG_TERM_GROWTH

        mix_broke -= amount_missing
        if amount_missing > 0:
            _, tax = roth_vs_traditional_effective_rate(amount_missing, 1)
            mix_broke -= tax
        mix_broke *= LONG_TERM_GROWTH
        mix_broke_inc = mix_broke * 0.7 * 0.03
        _, tax = roth_vs_traditional_effective_rate(mix_broke_inc, 1)
        mix_broke += mix_broke_inc - tax

        if mix_broke < 0.0:
            mix_broke = 0.0

        mixed_brokerage.append(mix_broke)
        mixed.append(invested_mix)

    return traditional_401k, roth_401k, missed_out_from_taxes, taxable_brokerage, total_tax_traditional, mixed, mixed_brokerage


def experiment_with_rmds():
    trad, roth, missed, broke, total_tax, _, _ = roth_vs_traditional(200000, 20000, 0.05, 36000)
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
    trad, _, _, broke, _, _, _ = roth_vs_traditional(60000, 2000, 0.05, 25000)
    combined = [t_val + broke[i] for i, t_val in enumerate(trad)]
    plt.plot(range(23, len(combined) + 23), combined)
    trad, _, _, broke, _, _, _ = roth_vs_traditional(60000, 3000, 0.05, 25000)
    combined = [t_val + broke[i] for i, t_val in enumerate(trad)]
    plt.plot(range(23, len(combined) + 23), combined)
    trad, _, _, broke, _, _, _ = roth_vs_traditional(60000, 4000, 0.05, 25000)
    combined = [t_val + broke[i] for i, t_val in enumerate(trad)]
    plt.plot(range(23, len(combined) + 23), combined)
    trad, _, _, broke, _, _, _ = roth_vs_traditional(100000, 4000, 0.05, 25000)
    combined = [t_val + broke[i] for i, t_val in enumerate(trad)]
    plt.plot(range(23, len(combined) + 23), combined)
    trad, _, _, broke, _, _, _ = roth_vs_traditional(200000, 4000, 0.05, 25000)
    combined = [t_val + broke[i] for i, t_val in enumerate(trad)]
    plt.plot(range(23, len(combined) + 23), combined)
    # trad, _, _, broke, _ = roth_vs_traditional(100000, 10000, 10000, 0.05, 30000)
    # combined = [t_val + broke[i] for i, t_val in enumerate(trad)]
    # plt.plot(range(23, len(combined) + 23), combined)

    plt.ylabel('Value of 401K')
    plt.xlabel('Age')
    plt.legend(
        ['$60K, $2K, $25K', '$60K, $3K, $25K', '$60K, $4K, $25K', '$100K, $4K, $25K', '$200K, $4K, $25K'])
    plt.title(f"Traditional 401K")
    plt.show()
    plt.close(fig)

def compare_roths():
    fig = plt.figure()
    _, roth, _, _, _, _, _ = roth_vs_traditional(60000, 2000, 0.05, 25000)
    plt.plot(range(23, len(roth) + 23), roth)
    _, roth, _, _, _, _, _ = roth_vs_traditional(60000, 3000, 0.05, 25000)
    plt.plot(range(23, len(roth) + 23), roth)
    _, roth, _, _, _, _, _ = roth_vs_traditional(60000, 4000, 0.05, 25000)
    plt.plot(range(23, len(roth) + 23), roth)
    _, roth, _, _, _, _, _ = roth_vs_traditional(100000, 4000, 0.05, 25000)
    plt.plot(range(23, len(roth) + 23), roth)
    _, roth, _, _, _, _, _ = roth_vs_traditional(200000, 4000, 0.05, 25000)
    plt.plot(range(23, len(roth) + 23), roth)
    # trad, _, _, broke, _ = roth_vs_traditional(100000, 10000, 10000, 0.05, 30000)
    # combined = [t_val + broke[i] for i, t_val in enumerate(trad)]
    # plt.plot(range(23, len(combined) + 23), combined)

    plt.ylabel('Value of 401K')
    plt.xlabel('Age')
    plt.legend(
        ['$60K, $2K, $25K', '$60K, $3K, $25K', '$60K, $4K, $25K', '$100K, $4K, $25K', '$200K, $4K, $25K'])
    plt.title(f"Roth 401K Performance")
    plt.show()
    plt.close(fig)


def compare_mixed():
    fig = plt.figure()
    trad, roth, _, broke, _, mixed, mix_broke = roth_vs_traditional(60000, 2000, 0.05, 25000)
    combined = [t_val + broke[i] for i, t_val in enumerate(trad)]
    plt.plot(range(23, len(combined) + 23), combined)
    plt.plot(range(23, len(roth) + 23), roth)
    mcombined = [t_val + mix_broke[i] for i, t_val in enumerate(mixed)]
    plt.plot(range(23, len(mcombined) + 23), mcombined)
    plt.ylabel('Value of 401K')
    plt.xlabel('Age')
    plt.legend(
        ['Traditional', 'Roth', 'Mixed Trad/Roth'])
    plt.title(f"Mixed 401K Performance ($60000, $2K/yr)")
    plt.show()
    plt.close(fig)

    fig = plt.figure()
    trad, roth, _, broke, _, mixed, mix_broke = roth_vs_traditional(80000, 5000, 0.05, 25000)
    combined = [t_val + broke[i] for i, t_val in enumerate(trad)]
    plt.plot(range(23, len(combined) + 23), combined)
    plt.plot(range(23, len(roth) + 23), roth)
    mcombined = [t_val + mix_broke[i] for i, t_val in enumerate(mixed)]
    plt.plot(range(23, len(mcombined) + 23), mcombined)
    plt.ylabel('Value of 401K')
    plt.xlabel('Age')
    plt.legend(
        ['Traditional', 'Roth', 'Mixed Trad/Roth'])
    plt.title(f"Mixed 401K Performance ($80000, $5K/yr)")
    plt.show()
    plt.close(fig)


def tax_rate_experiment():
    incomes = [5000, 10000, 15000, 20000, 30000, 50000, 75000, 100000, 150000, 200000, 300000, 400000,
            600000, 800000, 1000000, 2000000, 5000000, 10000000]

    tax_full = []
    for year in range(2):
        taxes = []
        for income in incomes:
            rate, _ = roth_vs_traditional_effective_rate(income, year)
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


# tax_rate_experiment()
# roth_vs_traditional_meh(200000,0,0,1)
# roth_vs_traditional(200000, 10000, 10000, 0.05, 24000)
# experiment_with_rmds()
compare_traditionals()
compare_roths()
compare_mixed()
