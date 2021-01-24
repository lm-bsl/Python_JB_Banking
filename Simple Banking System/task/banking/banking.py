# Write your code here
import random
import sqlite3

class CustomerAccount:
    all_accounts = []
    start_number = 493832089
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()
    conn.commit()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY AUTOINCREMENT, number TEXT, pin TEXT, balance INTEGER DEFAULT 0); ")
    conn.commit()

    def __init__(self):
        self.pin = None
        self.account_number = None
        self.card_number = None
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        CustomerAccount.all_accounts.append(self)
        CustomerAccount.start_number = CustomerAccount.start_number + 1

    def create_account(self):
        iin = 400000
        fill = 0
        account_width = 9
        account = random.randint(0, 999999999)
        self.account_number = str(f"{account:{fill}{account_width}}")
        self.card_number = str(f"{iin}{self.account_number}")
        card_sum = 0
        count = 0
        for number in str(self.card_number):
            if count % 2 == 0:
                number = int(number) * 2
            if int(number) > 9:
                number -= 9
            count += 1
            card_sum += int(number)

        if int(card_sum) % 10 == 0:
            checksum = "0"
        else:
            checksum = str(10 - (int(card_sum) % 10))
        self.card_number = str(f"{iin}{self.account_number}{checksum}")
        pin = random.randint(1000, 9999)
        fill = 0
        pin_width = 4
        self.pin = f"{pin:{fill}{pin_width}}"
        self.save_to_sql()
        return self

    def save_to_sql(self):
        self.cur.execute(f"INSERT INTO card (number, pin) VALUES({self.card_number}, {self.pin});")
        self.conn.commit()

    def add_income(self, logged_user, income):
        self.cur.execute(f"UPDATE card SET balance = balance + {income} WHERE number  = {logged_user} ;")
        self.conn.commit()
        return "Income was added!"

    def transfer(self, from_account, to_account, amount):
        var_check = CustomerAccount().check_card(to_account)
        var_creation = CustomerAccount().check_card_creation(to_account)
        if var_check & var_creation:
            if int(CustomerAccount().balance(from_account)) >= int(amount):
                self.cur.execute(f"UPDATE card SET balance = balance - {amount} WHERE number  = {from_account} ;")
                # add
                self.cur.execute(f"UPDATE card SET balance = balance + {amount} WHERE number  = {to_account} ;")
                self.conn.commit()
                print("Success!")
            else:
                print("Not enough Money")
        else:
            print("Probably you made a mistake in the card number. Please try again!")

    def check_card(self, card):
        count = 0
        card_sum = 0
        for number in str(card[:-1]):
            if count % 2 == 0:
                number = int(number) * 2
            if int(number) > 9:
                number -= 9
            count += 1
            card_sum += int(number)
        if int(card_sum) % 10 == 0:
            checksum = 0
        else:
            checksum = 10 - (int(card_sum) % 10)

        if int(card) == int(f"{card[:-1]}{checksum}"):
            return True
        else:
            return False

    def check_card_creation(self, card):
        q = self.cur.execute(f"SELECT COUNT(1) FROM card WHERE number = {card};")
        result = sum(q.fetchone())
        if result == 1:
            return True
        else:
            return False

    def login(self, card, pin):
        q = self.cur.execute(f"SELECT COUNT(1) FROM card WHERE number = {card} AND pin = {pin};")
        result = sum(q.fetchone())
        print(result)
        if result == 1:
            return True
        else:
            return False

    def balance(self, card):
        q = self.cur.execute(f"SELECT balance FROM card WHERE number = {card};")
        return sum(q.fetchone())

    def delete_account(self, card):
        self.cur.execute(f"DELETE FROM card WHERE number = {card};")
        self.conn.commit()


class Interface:
    def __init__(self):
        self.balance = 0
        self.logged_user = None
        self.system = CustomerAccount()

    def start_menu(self):
        if self.logged_user is None:
            print("1. Create an account")
            print("2. Log into account")
            print("0. Exit")
            choice = input(">")
            if int(choice) == 1:
                self.show_menu(1)
            elif int(choice) == 2:
                self.show_menu(2)
            elif int(choice) == 0:
                self.show_menu(5)
        else:
            print("1. Balance")
            print("2. Add income")
            print("3. Do transfer")
            print("4. Close account")
            print("5. Log out")
            print("0. Exit")
            choice = input(">")
            if int(choice) == 1:
                self.show_menu(3)  # Show Balance
            elif int(choice) == 2:
                self.show_menu(6)  # Add income
            elif int(choice) == 3:
                self.show_menu(7)  # Do transfer
            elif int(choice) == 4:
                self.show_menu(8)  # Close Account
            elif int(choice) == 5:
                self.show_menu(4)  # Log out
            elif int(choice) == 0:
                self.show_menu(5)  # Exit

    def show_menu(self, page):
        if page == 1:
            created_account = CustomerAccount().create_account()
            print(created_account.card_number)
            print(created_account.pin)

        elif page == 10:
            new_card = CustomerAccount()
            new_card.create_account()
            print(new_card.card_number)
            print(new_card.pin)

        elif page == 2:
            print("Enter your card number:")
            input_card: str = input(">")
            print("Enter your PIN:")
            input_pin: str = input(">")
            check_login = CustomerAccount().login(input_card, input_pin)
            if check_login:
                self.logged_user = input_card
                print("You have successfully logged in!")
            else:
                print("Wrong card number or PIN!")

        elif page == 3:
            balance = CustomerAccount().balance(self.logged_user)
            print(f"Balance:{balance}")

        elif page == 4:
            self.logged_user = None
            print("You have successfully logged out!")
        elif page == 6:
            print("Enter income:")
            income: int = input(">")
            logged_user = self.logged_user
            result = CustomerAccount().add_income(logged_user, income)
            print(result)  # add income

        elif page == 7:
            print("Transfer")
            print("Enter card number")
            card: str = input(">")
            if self.system.check_card(card):
                if self.system.check_card_creation(card):
                    print("Enter how much money you want to transfer:")
                    money_to_transfer: int = int(input(">"))
                    CustomerAccount().transfer(self.logged_user, card, money_to_transfer)
                else:
                    print("Such card do not exist")
            else:
                print("Probably you made a mistake in the card number. Please try again!")
        elif page == 8:
            self.system.delete_account(self.logged_user)
            print("The account has been closed!")
        elif page == 5:
            print("Bye!")
            quit()
        self.start_menu()


run = Interface()

run.start_menu()