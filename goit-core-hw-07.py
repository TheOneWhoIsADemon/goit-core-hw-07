from collections import UserDict
from datetime import datetime, timedelta


class Field:
     # Базовий клас для зберігання полів контакту (ім'я, телефон, день народження)

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    # Клас для зберігання імені контакту.
    pass

class Phone(Field):
    # Клас для зберігання телефонних номерів із перевіркою формату (10 цифр).
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Номер телефону має містити рівно 10 цифр")
        super().__init__(value)

class Birthday(Field):
    # Клас для зберігання дня народження у форматі ДД.ММ.РРРР.
    def __init__(self, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')  # Перевірка формату
            super().__init__(value)
        except ValueError:
            raise ValueError("Дата народження повинна бути у форматі ДД.ММ.РРРР")

class Record:
    """
    Клас для зберігання інформації про контакт:
    - ім'я
    - список телефонів
    - день народження
    """
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        #Додає телефон до контакту
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        #Видаляє телефон із контакту
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError("Номер телефону не знайдено")

    def edit_phone(self, old_phone, new_phone):
        # Редагує існуючий телефон
        phone_obj = self.find_phone(old_phone)
        if phone_obj:
            self.add_phone(new_phone)
            self.remove_phone(old_phone)
        else:
            raise ValueError("Старий номер телефону не знайдено")

    def find_phone(self, phone):
        # Шукає телефон у списку
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        # Додає або оновлює день народження
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        #Розраховує кількість днів до наступного дня народження
        if not self.birthday:
            return None

        today = datetime.today().date()
        birthday_date = datetime.strptime(self.birthday.value, '%d.%m.%Y').date()
        next_birthday = birthday_date.replace(year=today.year)

        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)

        if next_birthday.weekday() in (5, 6):  # Перенос на понеділок
            next_birthday += timedelta(days=(7 - next_birthday.weekday()))

        return (next_birthday - today).days

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        birthday = f", birthday: {self.birthday.value}" if self.birthday else ''
        return f"Contact name: {self.name.value}, phones: {phones}{birthday}"

class AddressBook(UserDict):
    # Клас для зберігання списку контактів (словник, де ключ - ім'я, а значення - Record)

    def add_record(self, record):
        #Додає контакт до адресної книги
        self.data[record.name.value] = record

    def find(self, name):
        #Шукає контакт за ім'ям
        return self.data.get(name, None)

    def delete(self, name):
        #Видаляє контакт за ім'ям
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Запис не знайдено")

    def upcoming_birthdays(self, days=7):
        #Повертає контакти з днями народження в межах найближчих N днів
        today = datetime.today().date()
        upcoming = []

        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, '%d.%m.%Y').date()
                next_birthday = birthday_date.replace(year=today.year)

                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)

                if next_birthday.weekday() in (5, 6):  # Перенос на понеділок
                    next_birthday += timedelta(days=(7 - next_birthday.weekday()))

                if (next_birthday - today).days <= days:
                    upcoming.append((record.name.value, next_birthday))

        return sorted(upcoming, key=lambda x: x[1])

    def __str__(self):
        # Повертає всі записи у вигляді рядка
        return '\n'.join(str(record) for record in self.data.values())


def input_error(func):
    #Декоратор для обробки помилок
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "This contact does not exist."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Invalid input. Please provide the required arguments."
    return inner

@input_error
def parse_input(user_input):
    # Розбиває введений рядок на команду та аргументи
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

@input_error
def add_contact(args, book):
    #Додає новий контакт
    name, phone = args
    record = book.find(name) or Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return f"Contact {name} added/updated."

@input_error
def add_birthday(args, book):
    #Додає день народження до контакту
    name, birthday = args
    record = book.find(name)
    if not record:
        raise KeyError("Contact not found.")
    record.add_birthday(birthday)
    return f"Added birthday for {name}."

@input_error
def show_phone(args, book):
    #Показує телефони контакту
    name, = args
    record = book.find(name)
    if not record:
        raise KeyError
    phones = ', '.join(phone.value for phone in record.phones)
    return f"{name}'s phones: {phones}."

@input_error
def change_phone(args, book):
    # Змінює телефон у контакті
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return f"Phone for {name} updated."

@input_error
def show_birthday(args, book):
    # Показує день народження контакту
    name, = args
    record = book.find(name)
    if not record or not record.birthday:
        raise KeyError("No birthday found.")
    return f"{name}'s birthday: {record.birthday.value}."

@input_error
def show_all(book):
    # Показує всі контакти
    return str(book) if book.data else "No contacts saved."

@input_error
def birthdays(book):
    # Показує контакти з найближчими днями народження
    upcoming = book.upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    return '\n'.join(f"{name} - {date.strftime('%d.%m.%Y')}" for name, date in upcoming)

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip()
        try:
            command, args = parse_input(user_input)

            if command in ["close", "exit"]:
                print("Good bye!")
                break
            elif command == "hello":
                print("How can I help you?")
            elif command == "add":
                print(add_contact(args, book))
            elif command == "add-birthday":
                print(add_birthday(args, book))
            elif command == "phone":
                print(show_phone(args, book))
            elif command == "all":
                print(show_all(book))
            elif command == "birthdays":
                print(birthdays(book))
            else:
                print("Invalid command.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()