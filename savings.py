from datetime import datetime
import pandas as pd

from constants import ALL, RETIREMENT, KID_EDUCATION, HOUSE, COMPUTER, CAR, PHONE, DRUMS

def flat_savings(starting_bal, years_until, monthly_input):
    def create_row(i, bal, income, cont):
        return [round(income,2), i+CURRENT_AGE, i, round(bal,2), round(cont,2), round(cont*12,2)]
    i = 0
    balance = starting_bal
    curr_income = CURRENT_INCOME
    # start a year in the past
    data_tracking = [create_row(-1, (starting_bal-monthly_input*12)/INVESTMENT_INTEREST_RATE, curr_income/INCOME_INFLATION_RATE, monthly_input)]
    while i < years_until:
        data_tracking.append(create_row(i, balance, curr_income, monthly_input))
        balance *= INVESTMENT_INTEREST_RATE
        balance += monthly_input*12
        curr_income *= INCOME_INFLATION_RATE
        i += 1
    data_tracking.append(create_row(i, balance, curr_income, monthly_input))
    return balance, data_tracking


def income_proportional_savings(starting_bal, years_until, yearly_percentage):
    def create_row(i, bal, income, pct):
        return [round(income,2), i+CURRENT_AGE, i, round(bal,2), round(income*pct/12,2), round(income*pct,2)]
    i = 0
    balance = starting_bal
    curr_income = CURRENT_INCOME
    # start a year in the past
    data_tracking = [create_row(-1, (balance-(curr_income/INCOME_INFLATION_RATE*yearly_percentage))/INVESTMENT_INTEREST_RATE, curr_income/INCOME_INFLATION_RATE, yearly_percentage)]
    while i < years_until:
        data_tracking.append(create_row(i, balance, curr_income, yearly_percentage))
        balance *= INVESTMENT_INTEREST_RATE
        balance += curr_income * yearly_percentage
        curr_income *= INCOME_INFLATION_RATE
        i += 1
    data_tracking.append(create_row(i, balance, curr_income, yearly_percentage))
    return balance, data_tracking


def binary_search_for_goal(goal, current_age, age_saving_for, curr_balance, money_summation_key = flat_savings, low_monthly_guess=0, high_monthly_guess=100_000):
    years_until = age_saving_for - current_age

    guess = (goal - curr_balance) / years_until
    low_guess = (low_monthly_guess, money_summation_key(curr_balance, years_until, low_monthly_guess)[0])
    high_guess = (high_monthly_guess, money_summation_key(curr_balance, years_until, high_monthly_guess)[0])

    while high_guess[1] - low_guess[1] > .01:

        balance, data = money_summation_key(curr_balance, years_until, guess)
        
        if balance - goal > 0 and balance - goal < high_guess[1] - goal:
            high_guess = (guess, balance)
        if balance - goal < 0 and balance - goal > low_guess[1] - goal:
            low_guess = (guess, balance)
        
        guess = (high_guess[0] + low_guess[0]) / 2
        
        # print(goal, balance, guess, high_guess, low_guess)
    return guess, data

if __name__ == "__main__":
    INVESTMENT_INTEREST_RATE = ALL['INVESTMENT_INTEREST_RATE']
    INCOME_INFLATION_RATE = ALL['INCOME_INFLATION_RATE']
    CURRENT_INCOME = ALL['CURRENT_INCOME']
    CURRENT_AGE = ALL["CURRENT_AGE"]
    dct = RETIREMENT

    flat_df = None
    prop_df = None

    for dct in (RETIREMENT, KID_EDUCATION, HOUSE, COMPUTER, CAR, PHONE, DRUMS):
        NAME = dct["NAME"]
        FN = dct["FN"]
        SAVING_GOAL = dct["SAVING_GOAL"]
        AGE_SAVING_FOR = dct["AGE_SAVING_FOR"]
        CURRENT_BALANCE = dct["CURRENT_BALANCE"]

        print(f"\nSaving for: {NAME}")
        monthly, data = binary_search_for_goal(SAVING_GOAL, CURRENT_AGE, AGE_SAVING_FOR, CURRENT_BALANCE, money_summation_key=flat_savings, high_monthly_guess=SAVING_GOAL)
        df = pd.DataFrame(data, columns=['income', 'age', 'year of saving', f'{NAME} saved', f'{NAME} monthly', f'{NAME} annual'])
        # df.to_csv(f"csvs/flat_{FN}", index=False)
        # print(df)
        print(f"Can use flat rate of ${monthly:,.2f} per month")

        if flat_df is None:
            flat_df = df
        else:
            flat_df = pd.merge(flat_df, df, 
                on=['income', 'age', 'year of saving'],
                how="outer"  # this matters a lot
            )



        percent, data = binary_search_for_goal(SAVING_GOAL, CURRENT_AGE, AGE_SAVING_FOR, CURRENT_BALANCE, money_summation_key=income_proportional_savings, high_monthly_guess=1)
        df = pd.DataFrame(data, columns=['income', 'age', 'year of saving', f'{NAME} saved', f'{NAME} monthly', f'{NAME} annual'])
        # df.to_csv(f"csvs/prop_{FN}", index=False)
        # print(df)
        print(f"or {percent :<.2%} of income (${CURRENT_INCOME*percent/12:,.2f} per month right now)")

        if prop_df is None:
            prop_df = df
        else:
            prop_df = pd.merge(prop_df, df, 
                on=['income', 'age', 'year of saving'],
                how="outer"  # this matters a lot
            )

    prop_df.to_csv("csvs/prop.csv", index=False)
    flat_df.to_csv("csvs/flat.csv", index=False)