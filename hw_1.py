from collections import UserDict
from datetime import datetime, date, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if value.isdigit() and len(value) == 10:
            super().__init__(value)
        else:
            raise ValueError("Phone number must contain exactly 10 digits")


class Birthday(Field):
    def __init__(self, value):
        try:
            parsed_value = datetime.strptime(value, '%d.%m.%Y')
            super().__init__(parsed_value)
        except ValueError:
            raise ValueError('Invalid date format. Use DD.MM.YYYY')


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        new_phone = Phone(phone)
        self.phones.append(new_phone)

    def remove_phone(self, phone):
        self.phones = [ph for ph in self.phones if phone != ph.value]

    def edit_phone(self, old_phone, new_phone):
        for index, ph in enumerate(self.phones):
            if ph.value == old_phone:
                self.phones[index] = Phone(new_phone)
                return
        raise ValueError("Phone number does not exist.")

    def find_phone(self, phone):
        result = list(filter(lambda ph: phone == ph.value, self.phones))
        return result[0] if len(result) > 0 else None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def date_to_string(self, date_obj):
        return date_obj.strftime('%d.%m.%Y')

    def find_next_weekday(self, start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)

    def adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 5:
            return self.find_next_weekday(birthday, 0)
        return birthday

    def get_upcoming_birthdays(self, days = 7):
        upcoming_birthdays = []
        today = date.today()
        for contact in self.data.values():
            try:
                birthday_this_year = contact.birthday.value.replace(year = today.year).date()
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year = today.year + 1)
                if 0 <= (birthday_this_year - today).days <= days:
                    upcoming_birthdays.append({
                        'name': contact.name.value, 'birthday':
                            self.date_to_string(self.adjust_for_weekend(birthday_this_year))
                    })
            except AttributeError:
                continue
        return upcoming_birthdays

    def __str__(self):
        address_book = ""
        for name, record in self.data.items():
            address_book += f'{record}\n'
        return address_book


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Enter the argument for the command."
        except KeyError:
            return "Contact not found."
        except AttributeError as e:
            if str(e):
                return str(e)
            return "Contact not found."
    return inner


@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args, book: AddressBook):
    record = book.find(args[0])
    if record is None:
        raise AttributeError
    return str(record)


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        raise AttributeError
    if birthday:
        record.add_birthday(birthday)
        return f"{name}\'s birthday info updated."


@input_error
def show_birthday(args, book: AddressBook):
    record = book.find(args[0])
    if record is None:
        raise AttributeError
    if record.birthday is None:
        raise AttributeError(f'{args[0]} does not have a birthday.')
    return book.date_to_string(record.birthday.value)


def birthdays(book: AddressBook):
    upcoming_str = ""
    for contact in book.get_upcoming_birthdays():
        upcoming_str += f"{contact['name']}: {contact['birthday']}\n"
    return upcoming_str


def show_all(book: AddressBook):
    return str(book)


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()