from prettytable import PrettyTable
import os
import datetime as dt
from prettytable import prettytable
from termcolor import colored
import json
from dateutil import parser
import re

TODAY = dt.datetime.today().date()


def clear_screen():
    # For Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # For Unix/Linux/MacOS
    else:
        _ = os.system('clear')


os.environ['TERM'] = 'xterm'


class ExpenseTracker:
    def __init__(self, user=None):

        self.user = user
        self.check_emptiness()

        self.user = user if user else "default_user"  # Assign a default username or handle authentication
        self.expense_report = ExpensesReport(self.user)
        self.expense_manager = ExpenseManager(self.user)
        self.user_table = PrettyTable()
        self.user_table.field_names = ["Name of the command", "Command"]
        self.user_table.padding_width = 5
        self.user_table.align["Command"] = 'c'
        self.user_table.add_rows([
            ['Add today\'s expenses', 1],
            ['Add expenses for selected day', 2],
            ['Display month data', 3],
            ['Get days report', 4],
            ['Log out', 'e']
        ])

    def check_emptiness(self):
        user_directory = 'users'
        user_file = f'{user_directory}/{self.user}.json'

        # Create the directory if it doesn't exist
        if not os.path.exists(user_directory):
            os.makedirs(user_directory)

        # Now proceed with the rest of your file handling
        try:
            with open(user_file, 'r'):
                pass
        except FileNotFoundError:
            self.initialize_file_with_format()

    def initialize_file_with_format(self):
        user_directory = 'users'
        if not os.path.exists(user_directory):
            os.makedirs(user_directory)

        user_file = f'{user_directory}/{self.user}.json'

        with open(user_file, 'w') as json_file:
            json_file.write('{}')  # Empty JSON object to initialize
        print(f"User file {user_file} created successfully.")


    def run(self):
        """
        Runs the expense tracking application in a loop until the user chooses to log out.

        Returns:
            bool: True if the user chooses to log out, False otherwise.
        """
        # Call check_emptiness here on the ExpenseManager instance (not a string)
        self.expense_manager.check_emptiness()

        while True:
            clear_screen()
            print(self.user_table)
            print()
            choice = input("Enter command: ")
            match choice:
                case '1':
                    self.expense_manager.add_expenses(str(TODAY))
                case '2':
                    self.expense_manager.add_expenses()
                case '3':
                    self.expense_report.display_month_data()
                case '4':
                    self.expense_report.days_report()
                case 'e':
                    return True
                case _:
                    clear_screen()
                    print("Invalid input.\n".upper())
                    input("Press to continue... ")


class ExpenseManager:
    def __init__(self, user):
        """
        Initializes a new ExpenseManager object.

        Parameters:
            user (str): The username of the current user.

        Returns:
            None

        Method initializes the attributes of the ExpenseManager object.
        """
        self.user = user
        self.expenses_table = PrettyTable()
        self.expenses_table.hrules = prettytable.ALL
        self.expenses_table.field_names = ["Category", "Command"]
        self.expenses_table.padding_width = 2
        self.expenses_table.align["Command"] = 'c'
        self.expenses_table.align["Category"] = 'l'
        self.expenses_table.add_rows([
            ['Food (including groceries, dining out, and takeout)', 1],
            ['Housing (rent or mortgage payments, utilities, maintenance)', 2],
            ['Transportation (gasoline, public transit, vehicle maintenance)', 3],
            ['Health and wellness (healthcare expenses, gym memberships, medications)', 4],
            ['Entertainment (movies, concerts, streaming services)', 5],
            ['Shopping (clothing, electronics, personal care products)', 6],
            ['Travel (flights, hotels, vacation activities)', 7],
            ['Utilities (electricity, water, internet, phone)', 8],
            ['Education (tuition, books, supplies)', 9],
            ['Debt payments (credit card bills, loans)', 10],
            ['Insurance (health, auto, home)', 11],
            ['Personal care (haircuts, spa treatments, grooming products)', 12],
            ['Gifts and donations (birthday presents, charity donations)', 13],
            ['Household supplies (cleaning products, toiletries)', 14],
            ['Other Expenses', 15],
            ['Cancel operation', 'cancel']
        ])

        self.expenses = [
            'Food',
            'Housing',
            'Transportation',
            'Health and wellness',
            'Entertainment',
            'Shopping',
            'Travel',
            'Utilities',
            'Education',
            'Debt payments',
            'Insurance',
            'Personal care',
            'Gifts and donations',
            'Household supplies',
            'Other Expenses'
        ]

    @staticmethod
    def get_date():
        while True:
            date_input = input("Enter date you want to add expenses to (e.g., '2024-05-31'): ")
            if date_input.lower().strip() == "exit":
                break
            try:
                date_obj = parser.parse(date_input).date()
                if date_obj > TODAY:
                    clear_screen()
                    print(f"Date {date_obj} is in the future. Please enter past or present date.")
                elif (TODAY - date_obj).days > 365:
                    clear_screen()
                    print(f"Date {date_obj} was more than a year ago. Please enter a recent date.")
                else:
                    return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                clear_screen()
                print("Invalid date format!".upper())
                print("Please enter a valid date in format YYYY-MM-DD.")
                print("If you want to cancel operation, enter 'exit'\n")

    @staticmethod
    def format_date(date):
        date_obj = dt.datetime.strptime(date, "%Y-%m-%d")
        return date_obj.strftime("%d %B %Y")

    @staticmethod
    def enter_amount():
        while True:
            try:
                amount = float(input("Enter amount of money you've spent: $").strip().lower())
            except ValueError:
                print("You should enter a number! (e.g - 8.50)\n")
                continue
            if amount < 0:
                print("Money you've spent should be a positive number!\n")
                continue
            return amount

    @staticmethod
    def check_command(comm):
        try:
            comm = int(comm)
        except ValueError:
            print("Command is not valid. Please enter a number from 1 to 15 or 'cancel' to cancel operation")
            return False
        if 1 <= comm <= 15:
            return comm
        print("There is only 15 commands. Enter a number from 1 to 15 or 'cancel' to cancel operation")
        return False

    def initialize_file_with_format(self):
        """
        Initialize the JSON file with a predefined format.

        Returns:
            None

        Method initializes the JSON file associated with the user with a predefined format.
        """
        with open(f'users/{self.user}.json', 'w') as json_file:
            data = {
                'date': {},
                'month': {}
            }
            json.dump(data, json_file, indent=4)

    def check_emptiness(self):
        """
        Check if the JSON file is empty or not in the desired format.

        Returns:
            None

        Method checks if the JSON file associated with the user is empty or not in the desired format.
        """
        try:
            with open(f'users/{self.user}.json', 'r') as json_file:
                try:
                    loaded_data = json.load(json_file)
                    if 'date' in loaded_data and 'month' in loaded_data \
                            and isinstance(loaded_data['date'], dict) \
                            and isinstance(loaded_data['month'], dict):
                        pass  # Data is in the desired format
                    else:
                        self.initialize_file_with_format()  # Reinitialize the file
                except json.JSONDecodeError:
                    self.initialize_file_with_format()  # File is empty or not valid JSON
        except FileNotFoundError:
            self.initialize_file_with_format()  # File doesn't exist, create with format

    def logo_table_expenses(self, date):
        """
        Display the logo and table of expenses.

        Parameters:
            date (str): The selected date.

        Returns:
            None

        Method displays the logo of the user and the table of expenses for the selected date.
        """
        clear_screen()
        print(self.expenses_table)
        print(f"SELECTED DATE - {date}")
        logo = colored(self.user, attrs={"bold"})
        print(f"Username: {logo}\n")

    def save_expense(self, expense, amount, date):
        """
        Save the expense to the JSON file.

        Parameters:
            expense (str): The expense category.
            amount (float): The amount spent.
            date (str): The date of the expense.

        Returns:
            None

        Method saves the expense and amount to the JSON file associated with the user.
        """
        # Read existing data from the JSON file
        try:
            with open(f"users/{self.user}.json", "r") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        # Extract month and year from the date
        date_obj = dt.datetime.strptime(date, "%Y-%m-%d")
        month_year = date_obj.strftime("%B %Y")

        # Update data for the specific date
        if 'date' not in data:
            data['date'] = {}
        if date in data['date']:
            # If expense already exists for the date, update the amount
            if expense in data['date'][date]:
                data['date'][date][expense] += amount
            else:
                # If expense doesn't exist for the date, add it
                data['date'][date][expense] = amount
        else:
            # If there is no existing data for the date, create a new entry
            data['date'][date] = {expense: amount}

        # Update data for the specific month
        if 'month' not in data:
            data['month'] = {}

        if month_year in data['month']:
            if 'expenses' in data['month'][month_year] and expense in data['month'][month_year]['expenses']:
                # If the expense exists for the month, update its amount
                data['month'][month_year]['expenses'][expense] += amount
            else:
                # If the expense doesn't exist for the month, create a new entry
                data['month'][month_year]['expenses'][expense] = amount
        else:
            # If month doesn't exist, create a new entry
            data['month'][month_year] = {'limit': None, 'expenses': {expense: amount}}

            # Write the updated data back to the JSON file
        with open(f"users/{self.user}.json", "w") as file:
            json.dump(data, file, indent=4)

    def add_expenses(self, date=""):
        """
        Add expenses for a specific date.

        Parameters:
            date (str, optional): The date to add expenses for. Defaults to "".

        Returns:
            None

        Method allows the user to add expenses for a specific date.
        """
        if date == "":
            date = self.get_date()
        if date is None:
            clear_screen()
            print("You have successfully canceled operation!\n")
            input("Press to continue...")
            return
        f_date = self.format_date(date)
        continue_adding = True
        while continue_adding:
            self.logo_table_expenses(f_date)
            correct_input = False
            while not correct_input:
                exp_choice = input("Enter which expense you want to add: ").lower().strip()
                if exp_choice == 'cancel':
                    return
                correct_input = self.check_command(exp_choice)
            clear_screen()
            print(f"You have selected {self.expenses[correct_input - 1]} expense.\n")
            amount = self.enter_amount()
            clear_screen()
            choice = input(f"Do you want to add {self.expenses[correct_input - 1]} "
                           f"expense with ${amount} of money spent at {f_date}? (y/n) ").lower().strip()
            while choice != 'y' and choice != 'n':
                print("You should enter only 'y' to save expense or 'n' to cancel it!")
                choice = input(f"Do you want to add {self.expenses[correct_input - 1]} "
                               f"expense with ${amount} of money spent at {f_date}?").lower().strip()
            if choice == 'n':
                print("Expense wasn't saved to your list!\n")
                continue
            self.save_expense(self.expenses[correct_input - 1], amount, date)
            print()
            choice = input("Do you want to add another expense? (y/n) ").strip().lower()
            while choice != 'y' and choice != 'n':
                print("Invalid input! Enter 'y' if you want to add another expense and 'n' if don't.")
                choice = input("Enter your choice: ").strip().lower()
            if choice == 'n':
                continue_adding = False
                continue
            else:
                print()

    def set_limit(self, select_month_func):
        """
        Set a spending limit for a specific month.

        Parameters:
            select_month_func (function): A function to select the month.

        Returns:
            None

        Method allows the user to set a spending limit for a specific month.
        """
        # Load data from JSON file
        with open(f"users/{self.user}.json", "r") as file:
            data = json.load(file)

        clear_screen()

        # Get the current month
        selected_month = select_month_func("set a limit for")

        clear_screen()

        while True:
            clear_screen()

            if 'limit' in data['month'].get(selected_month, {}):
                print(f"The limit for {selected_month} is ${data['month'][selected_month]['limit']}\n")

            limit_input = input(f"Enter the new limit for {selected_month} (type 'cancel' to cancel): ")

            if limit_input.lower() == 'cancel':
                print("Operation cancelled.")
                return

            try:
                new_limit = float(limit_input)
            except ValueError:
                clear_screen()
                print("Invalid input! Please enter a number.")
                input("Press to continue...")
                continue  # Restart the loop to prompt the user again

            # Add or update the limit for the selected month
            data['month'].setdefault(selected_month, {})['limit'] = new_limit

            # Check if there are expenses for the selected month
            if 'expenses' not in data['month'][selected_month]:
                data['month'][selected_month]['expenses'] = {}

            # Write the updated data back to the JSON file
            with open(f"users/{self.user}.json", "w") as file:
                json.dump(data, file, indent=4)
            break  # Exit the loop if input is valid


class ExpensesReport:

    def __init__(self, user):
        """
        Initialize an ExpensesReport object.

        Parameters:
            user (str): The username associated with the report.

        Returns:
            None

        Method initializes an ExpensesReport object with a PrettyTable for displaying report commands.
        """
        self.user = user
        self.report_table = PrettyTable()
        self.report_table.field_names = ["Name of the command", "Command"]
        self.report_table.padding_width = 5
        self.report_table.align["Command"] = 'c'
        self.report_table.add_rows([
            ["Send this month report", 1],
            ["Send selected month report", 2],
            ["Sent days report", 3],
            ["Cancel report sending", 'e']
        ])

    @staticmethod
    def select_another_month(message):
        clear_screen()
        while True:
            user_input = input(f"Enter the month you want to {message} (e.g., 'May 2024'): ").strip()
            try:
                formatted_month = dt.datetime.strptime(user_input, "%B %Y").strftime("%B %Y")
                return formatted_month
            except ValueError:
                clear_screen()
                print(
                    "Invalid input! "
                    "Please enter the month and year in the format 'Month Year' (e.g., 'May 2024')\n")

    def select_month(self, message):
        """
        Prompt the user to select a month.

        Parameters:
            message (str): The message indicating the action to be performed.

        Returns:
            str: The selected month in the format 'Month Year'.

        Method prompts the user to either select the current month or another month.
        """

        current_month = dt.datetime.now().strftime("%B %Y")
        change_month = input(
            f"Do you want to {message} {current_month}? (y/n): ").lower().strip()
        if change_month == 'y':
            return current_month
        elif change_month == 'n':
            return self.select_another_month(message)
        else:
            clear_screen()
            print(f"Invalid data! Please enter 'y' or 'n'\n")
            return self.select_month(message)

    @staticmethod
    def get_date_range(prompt):
        while True:
            date_input = input(prompt)
            if date_input.lower().strip() == "cancel":
                return None
            try:
                date_obj = parser.parse(date_input).date()
                if date_obj > TODAY:
                    clear_screen()
                    print(f"Date {date_obj} is in the future. Please enter past or present date.")
                    continue
                elif (TODAY - date_obj).days > 365:
                    clear_screen()
                    print(f"Date {date_obj} was more than a year ago. Please enter a recent date.")
                    continue
                else:
                    return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                clear_screen()
                print("Invalid date format!".upper())
                print("Please enter a valid date in format YYYY-MM-DD.")
                print("If you want to cancel operation, enter 'cancel'\n")

    @staticmethod
    def get_user_address():
        while True:
            address = input("Enter your address: ")
            if re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', address):
                return address
            else:
                print("Invalid address format. Please try again.")

    @staticmethod
    def get_month_report_info(month_data):
        report_info = []

        total_amount = 0
        num_expenses = len(month_data.get('expenses', {}))

        if num_expenses >= 3:
            table = PrettyTable(["Category", "Price"])

            # Adjust padding width for consistent spacing
            table.padding_width = 2

            # Set alignment for columns
            table.align["Price"] = "r"  # Right align Price column
            table.align["Category"] = 'l'  # Left align Category column

            for expense, amount in month_data['expenses'].items():
                table.add_row([expense, f"${amount:.2f}"])
                total_amount += amount

            table.add_row(["-" * 30, "-" * 10])  # Adjust as needed
            table.add_row(["Total", f"${total_amount:.2f}"])

            report_info.append(table)
        else:
            expenses_info = "\n".join([f"{expense}: ${amount:.2f}"
                                       for expense, amount in month_data.get('expenses', {}).items()])
            report_info.append("Expenses:\n" + expenses_info)

            total_amount = sum(month_data.get('expenses', {}).values())
            if num_expenses > 1:
                report_info.append(f"Total: ${total_amount:.2f}")

        if 'limit' in month_data and isinstance(month_data['limit'], float):
            limit = month_data['limit']
            report_info.append(f"Limit: ${limit:.2f}")
            amount_available = limit - total_amount
            report_info.append(f"Amount available: ${amount_available:.2f}")
        else:
            report_info.append("No limit set for this month.")

        return "\n\n".join([str(table) for table in report_info])

    def short_month_data(self):
        """
        Display short data for the selected month.

        Returns:
            None

        Method displays short data for the selected month, including total amount spent and limit information.
        """

        # Load data from JSON file
        with open(f"users/{self.user}.json", "r") as file:
            data = json.load(file)

        clear_screen()

        selected_month = self.select_month("get information about")

        clear_screen()

        # Extract data for the current month
        selected_month_data = data['month'].get(selected_month)

        if selected_month_data is None:
            print(f"No data found for {selected_month}.\n")
            input("Press to continue...")
            return

        # Get the limit for the current month, if set
        limit = selected_month_data.get('limit')

        # Calculate total amount spent
        expenses_only = selected_month_data.get('expenses', {})
        total_spent = sum(expenses_only.values())

        # Print results
        print(f"Total amount spent in {selected_month}: ${total_spent:.2f}")
        if limit and isinstance(limit, float):
            print(f"Limit set for {selected_month}: ${limit:.2f}")
            amount_available = limit - total_spent
            print(f"Amount available: ${amount_available:.2f}")
        else:
            print("No limit set for this month.")

        input("Press to continue...")

    def get_month_data(self, s_month):
        """
        Get data for the selected month.

        Parameters:
            s_month (str): The selected month.

        Returns:
            dict: Data for the selected month.

        Method retrieves data for the selected month from the JSON file.
        """
        # Load data from JSON file
        with open(f"users/{self.user}.json", "r") as file:
            data = json.load(file)

        # Extract data for the selected month
        return data['month'].get(s_month)

    def display_month_data(self):
        """
        Display detailed data for the selected month.

        Returns:
            None

        Method displays detailed data for the selected month, including expenses and limit information.
        """
        selected_month = self.select_month("display data for")

        month_data = self.get_month_data(selected_month)

        # Check if data exists for the selected month
        if month_data:
            clear_screen()
            print(f"Month: {selected_month}")

            report_info = self.get_month_report_info(month_data)
            print(report_info)
        else:
            clear_screen()
            print(f"No data found for {selected_month}.\n")

        input("Press to continue...")

    @staticmethod
    def calculate_category_totals(data, start_date, end_date):
        category_totals = {}
        current_date = end_date
        while current_date >= start_date:
            current_date_str = current_date.strftime("%Y-%m-%d")
            if current_date_str in data['date']:
                expenses_for_date = data['date'][current_date_str]
                for category, amount in expenses_for_date.items():
                    category_totals[category] = category_totals.get(category, 0) + amount
            current_date -= dt.timedelta(days=1)
        return category_totals

    def days_report(self):
        """
        Display the days report.

        Returns:
            None

        Method displays the days report, including expenses for each day and category totals.
        """
        with open(f"users/{self.user}.json", "r") as file:
            data = json.load(file)

        clear_screen()

        start_date = self.get_date_range("Enter start date for the expense report (e.g., '2024-04-01'): ")

        if start_date is None:
            print("You have canceled action!\n")
            input("Press to continue...")
            return

        end_date = self.get_date_range("Enter end date for the expense report (e.g., '2024-04-01'): ")

        if end_date is None:
            print("You have canceled action!\n")
            input("Press to continue...")
            return

        start_date = dt.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end_date, "%Y-%m-%d")

        category_totals = self.calculate_category_totals(data, start_date, end_date)

        current_date = end_date

        start_date_str = start_date.strftime("%d %B %Y")
        end_date_str = end_date.strftime("%d %B %Y")

        clear_screen()
        print(f"Expenses report for time period from {start_date_str} to {end_date_str}")

        while current_date >= start_date:
            current_date_str = current_date.strftime("%Y-%m-%d")
            if current_date_str in data['date']:
                expenses_for_date = data['date'][current_date_str]
                print()
                print("----------------------------------------------------------------------------------")
                print(f"{current_date.strftime('%d %B %Y')} expenses:")
                for category, amount in expenses_for_date.items():
                    print(f"  {category}: ${amount:.2f}")
            current_date -= dt.timedelta(days=1)

        print("----------------------------------------------------------------------------------")
        print("\nTotal expenses for each category:")
        for category, total in category_totals.items():
            print(f"  {category}: ${total:.2f}")

        total_all_expenses = sum(category_totals.values())
        print(f"\nTotal for all expenses: ${total_all_expenses:.2f}")

        print()
        input("Press to continue...")


# Create an instance without specifying a username
expense_tracker = ExpenseTracker(user='default')

# Run the expense tracker
expense_tracker.run()
