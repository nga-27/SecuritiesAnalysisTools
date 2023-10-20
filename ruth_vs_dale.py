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
import random
import matplotlib.pyplot as plt

BASE_GROWTH = 0.05
OTHER_GROWTH = 0.06 # Since 1950, 8% has been the mean return of the S&P500
ANNUAL_CONTRIBUTION = 12000.0
START_AGE = 23.0


def basic_ruth_vs_dale():
    # index 0 is end of first year of working, so end of 23 years old, for math purposes. Each year
    # will be 12 indexes, as we will be looking at months (0.05/12)
    ruth = [0.0]
    dale = [0.0]
    age = [START_AGE]
    crossover = START_AGE
    for i in range(12 * 42):
        if i < 120:
            ruth_new = ruth[-1] * (1.0 + BASE_GROWTH / 12.0) + (ANNUAL_CONTRIBUTION / 12.0)
            ruth.append(ruth_new)
            dale.append(0.0)
        else:
            ruth_new = ruth[-1] * (1.0 + BASE_GROWTH / 12.0)
            ruth.append(ruth_new)
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
    plt.title(f"Ruth vs. Dale 5% Growth (Crossover at age {crossover})")
    plt.show()
    plt.close(fig)


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
    plt.legend(['Ruth @ 8%', 'Dale @ 8%'])
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


basic_ruth_vs_dale_adjusted(0.04)
basic_ruth_vs_dale_adjusted(0.05)
basic_ruth_vs_dale_adjusted(0.06)
basic_ruth_vs_dale_adjusted(0.0625)
basic_ruth_vs_dale_adjusted(0.07)
basic_ruth_vs_dale_adjusted(0.08)
basic_ruth_vs_dale_without_stopping()
stochastic_basic()
