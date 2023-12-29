from datetime import datetime

INVESTMENT_INTEREST_RATE = 1.06
INCOME_INFLATION_RATE = 1.03
CURRENT_INCOME = 103600
SAVING_GOAL = 6_000_000
DATE_SAVING_FOR =  "06/15/2067"
CURRENT_BALANCE = 30_000

def flat_savings(starting_bal, months_until, monthly_input):
    i = 0
    balance = starting_bal
    while i < months_until:
        balance *= 1 + ((INVESTMENT_INTEREST_RATE - 1) / 12)
        balance += monthly_input
        i += 1
    return balance


def income_proportional_savings(starting_bal, months_until, monthly_percentage):
    i = 0
    balance = starting_bal
    curr_income = CURRENT_INCOME
    while i < months_until:
        balance *= 1 + ((INVESTMENT_INTEREST_RATE - 1) / 12)
        balance += curr_income * monthly_percentage
        curr_income *= 1 + ((INCOME_INFLATION_RATE - 1) / 12)
        i += 1
    return balance


def binary_search_for_goal(goal, date, curr_balance, money_summation_key = flat_savings, low_monthly_guess=0, high_monthly_guess=100_000):
    months_until = int( (date - datetime.now()).total_seconds() / 60 / 60 / 24 / (365/12) )

    monthly_guess = (goal - curr_balance) / months_until
    low_guess = (low_monthly_guess, money_summation_key(curr_balance, months_until, low_monthly_guess))
    high_guess = (high_monthly_guess, money_summation_key(curr_balance, months_until, high_monthly_guess))

    while high_guess[1] - low_guess[1] > .01:

        balance = money_summation_key(curr_balance, months_until, monthly_guess)
        
        if balance - goal > 0 and balance - goal < high_guess[1] - goal:
            high_guess = (monthly_guess, balance)
        if balance - goal < 0 and balance - goal > low_guess[1] - goal:
            low_guess = (monthly_guess, balance)
        
        monthly_guess = (high_guess[0] + low_guess[0]) / 2
        
        # print(goal, balance, monthly_guess, high_guess, low_guess)
    return monthly_guess

if __name__ == "__main__":

    monthly = binary_search_for_goal(SAVING_GOAL, datetime.strptime(DATE_SAVING_FOR, "%M/%d/%Y"), CURRENT_BALANCE, money_summation_key=flat_savings, high_monthly_guess=SAVING_GOAL)
    print(monthly)
    percent = binary_search_for_goal(SAVING_GOAL, datetime.strptime(DATE_SAVING_FOR, "%M/%d/%Y"), CURRENT_BALANCE, money_summation_key=income_proportional_savings, high_monthly_guess=1)
    print(f"{percent :<.2%}")
