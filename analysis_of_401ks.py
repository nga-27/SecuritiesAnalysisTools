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


def roth_vs_traditional(max_income: int, trad_pct: float, roth_pct: float, tax_year: int):
    MAX_YR_CAREER = 43
    x = np.linspace(1, MAX_YR_CAREER)
    income = np.log(x) / np.log(MAX_YR_CAREER) * (max_income / 2) + (max_income / 2)

    # fig = plt.figure()
    # plt.plot(x, income)
    # plt.show()
    # plt.close(fig)


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


tax_rate_experiment()
roth_vs_traditional(200000,0,0,0,0)
