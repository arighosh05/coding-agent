import time
from calendar import isleap

def is_leap_year(year):
    """Returns True if the given year is a leap year, otherwise False."""
    return isleap(year)

def get_days_in_month(month, leap_year):
    """Returns the number of days in the given month, considering leap years for February."""
    days_in_month = {1: 31, 2: 29 if leap_year else 28, 3: 31, 4: 30, 5: 31, 6: 30,
                     7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    return days_in_month.get(month, 0)  # Default to 0 if an invalid month is passed

def get_age_details(name, age):
    """Calculates the age in years, months, and days."""
    try:
        age = int(age)  # Validate numeric input
    except ValueError:
        print("Invalid age. Please enter a numeric value.")
        return

    # Get the current local time
    current_time = time.localtime()
    birth_year = current_time.tm_year - age
    birth_month = current_time.tm_mon
    birth_day = current_time.tm_mday

    # Compute total months and total days
    total_months = age * 12 + birth_month
    total_days = 0

    # Count full years in days
    for year in range(birth_year, birth_year + age):
        total_days += 366 if is_leap_year(year) else 365

    # Count months of the current year in days
    for month in range(1, birth_month):
        total_days += get_days_in_month(month, is_leap_year(current_time.tm_year))

    # Add remaining days
    total_days += birth_day

    # Print the result
    print(f"{name}'s age is {age} years or {total_months} months or {total_days} days")

if __name__ == "__main__":
    user_name = input("Enter your name: ").strip()
    user_age = input("Enter your age: ").strip()
    get_age_details(user_name, user_age)
