from datetime import datetime
import pandas as pd

from constants import ALL, RETIREMENT, KID_EDUCATION, HOUSE

def flat_savings(starting_bal, years_until, monthly_input):
    i = 0
    balance = starting_bal
    # start a year in the past
    data_tracking = [[-1+CURRENT_AGE, (starting_bal-monthly_input*12)/INVESTMENT_INTEREST_RATE, monthly_input, monthly_input*12],]
    while i < years_until:
        data_tracking.append([i+CURRENT_AGE, balance, monthly_input, monthly_input*12])
        balance *= INVESTMENT_INTEREST_RATE
        balance += monthly_input*12
        i += 1
    data_tracking.append([i+CURRENT_AGE, balance, monthly_input, monthly_input*12])
    return balance, pd.DataFrame(data_tracking, columns=['age', 'money saved', 'monthly input', 'annual input'])


def income_proportional_savings(starting_bal, years_until, yearly_percentage):
    i = 0
    balance = starting_bal
    curr_income = CURRENT_INCOME
    # start a year in the past
    data_tracking = [[-1+CURRENT_AGE, (balance-(curr_income/INCOME_INFLATION_RATE*yearly_percentage))/INVESTMENT_INTEREST_RATE, curr_income/INCOME_INFLATION_RATE*yearly_percentage/12, curr_income/INCOME_INFLATION_RATE*yearly_percentage],]
    while i < years_until:
        data_tracking.append([i+CURRENT_AGE, balance, yearly_percentage*curr_income/12, yearly_percentage*curr_income])
        balance *= INVESTMENT_INTEREST_RATE
        balance += curr_income * yearly_percentage
        curr_income *= INCOME_INFLATION_RATE
        i += 1
    data_tracking.append([i+CURRENT_AGE, balance, yearly_percentage*curr_income/12, yearly_percentage*curr_income])
    return balance, pd.DataFrame(data_tracking, columns=['age', 'money saved', 'monthly input', 'annual input'])


def binary_search_for_goal(goal, current_age, age_saving_for, curr_balance, money_summation_key = flat_savings, low_monthly_guess=0, high_monthly_guess=100_000):
    years_until = age_saving_for - current_age

    guess = (goal - curr_balance) / years_until
    low_guess = (low_monthly_guess, money_summation_key(curr_balance, years_until, low_monthly_guess)[0])
    high_guess = (high_monthly_guess, money_summation_key(curr_balance, years_until, high_monthly_guess)[0])

    while high_guess[1] - low_guess[1] > .01:

        balance, df = money_summation_key(curr_balance, years_until, guess)
        
        if balance - goal > 0 and balance - goal < high_guess[1] - goal:
            high_guess = (guess, balance)
        if balance - goal < 0 and balance - goal > low_guess[1] - goal:
            low_guess = (guess, balance)
        
        guess = (high_guess[0] + low_guess[0]) / 2
        
        # print(goal, balance, guess, high_guess, low_guess)
    return guess, df

if __name__ == "__main__":
    INVESTMENT_INTEREST_RATE = ALL['INVESTMENT_INTEREST_RATE']
    INCOME_INFLATION_RATE = ALL['INCOME_INFLATION_RATE']
    CURRENT_INCOME = ALL['CURRENT_INCOME']

    dct = RETIREMENT
    SAVING_GOAL = dct["SAVING_GOAL"]
    AGE_SAVING_FOR = dct["AGE_SAVING_FOR"]
    CURRENT_AGE = dct["CURRENT_AGE"]
    CURRENT_BALANCE = dct["CURRENT_BALANCE"]

    monthly, df = binary_search_for_goal(SAVING_GOAL, CURRENT_AGE, AGE_SAVING_FOR, CURRENT_BALANCE, money_summation_key=flat_savings, high_monthly_guess=SAVING_GOAL)
    print(f"${monthly:,.2f}")
    # print(df)
    percent, df = binary_search_for_goal(SAVING_GOAL, CURRENT_AGE, AGE_SAVING_FOR, CURRENT_BALANCE, money_summation_key=income_proportional_savings, high_monthly_guess=1)
    print(f"{percent :<.2%}")
    # print(df)
