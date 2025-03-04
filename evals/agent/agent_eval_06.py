from datetime import datetime
from calendar import isleap

class AgeCalculator:
    def __init__(self, name, age):
        self.name = name
        self.age_years = age

    @staticmethod
    def is_leap_year(year):
        """Determine if the specified year is a leap year."""
        return isleap(year)

    @staticmethod
    def days_in_month(month, year):
        """Return the number of days in a month, accounting for leap years."""
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        elif month == 2:
            return 29 if isleap(year) else 28

    def calculate_age_in_days(self):
        """Calculate the age in days based on years lived and the current date."""
        days = 0
        current_date = datetime.now()

        # Calculate full years days
        for year in range(current_date.year - self.age_years, current_date.year):
            days += 366 if self.is_leap_year(year) else 365

        # Calculate days for the current year's months
        for month in range(1, current_date.month):
            days += self.days_in_month(month, current_date.year)

        # Add the days passed in the current month
        days += current_date.day

        return days

    def display_age(self):
        """Display the age in years, months, and days."""
        months = self.age_years * 12 + datetime.now().month
        days = self.calculate_age_in_days()
        print(f"{self.name}'s age is {self.age_years} years or {months} months or {days} days.")


def main():
    while True:
        name = input("Input your name: ")
        try:
            age = int(input("Input your age: "))
            if age < 0 or age > 120:
                print("Please enter a realistic age.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    person = AgeCalculator(name, age)
    person.display_age()

if __name__ == "__main__":
    main()
