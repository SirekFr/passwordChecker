import requests
import hashlib
import sys
import smtplib
from email.message import EmailMessage
from string import Template
from pathlib import Path
import os


def send_email(message, address):
    """
    Constructs and sends email containing leaked password info
    :param message:
    :param address:
    """
    path_to_index = Path(__file__).parent / "index.html"
    html = Template(path_to_index.read_text())

    email = EmailMessage()
    email['from'] = 'passwordChecker'
    email['to'] = f'{address}'
    email['subject'] = 'Password Check'

    email.set_content(html.substitute({'message': message}), 'html')

    with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login('snekpako@gmail.com', 'otouduxieklebkor')
        smtp.send_message(email)
        print('Mail sent')


def request_api_data(query_char):
    url = 'https://api.pwnedpasswords.com/range/' + query_char
    res = requests.get(url)
    if res.status_code != 200:
        raise RuntimeError(f'Error fetching: {res.status_code}')
    return res


def get_password_leaks_count(hashes, hash_to_check):
    hashes = (line.split(':') for line in hashes.text.splitlines())
    for h, count in hashes:
        if h == hash_to_check:
            return count
    return 0


def generate_hash(password):
    """
    :param password:
    :return: hashed[head, tail]
    """
    sha1password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    hashed = [sha1password[:5], sha1password[5:]]
    return hashed


def pwnd_api_check(password):
    hashed = generate_hash(password)
    response = request_api_data(hashed[0])
    return get_password_leaks_count(response, hashed[1])


def file_mode(args):
    """
    checks saved passwords for leaks
    :param args:
    :return: message_string: info on leaked passwords
    """
    try:
        save_file_path = Path(__file__).parent / "saved.txt"
        with open(save_file_path, mode='r') as saved_file:
            lines = saved_file.readlines()
            message_string = ""
            if not lines:
                return "No saved passwords"
            for line in lines:
                saved_hash = line.rsplit(' ')
                response = request_api_data(saved_hash[0])
                leaks_count = get_password_leaks_count(response, saved_hash[1])

                first_two_letters = saved_hash[2].replace('\n', '')
                message_string += (f"Password starting with {first_two_letters}, "
                                   f"has been leaked {leaks_count} times.\n<br>")
            return message_string
    except FileNotFoundError as err:
        print('file does not exist')
        raise err


def save_passwords(args):
    """
    saves hashed password to a file, together with first two letters of password as identifiers
    :param args:
    """
    try:
        with open('saved.txt', mode='a') as saved_file:
            for password in args[1:]:
                hashed = generate_hash(password)
                first_two = password[:2]
                saved_file.write(f'{hashed[0]} {hashed[1]} {first_two}\n')
    except FileNotFoundError as err:
        print('file does not exist')
        raise err


def create_task(args):
    """
    Creates a daily task in windows task scheduler
    :param args:
    :return: "Done"
    """
    bat_file_address = Path(__file__).parent / "starttask.bat"
    with open(bat_file_address, mode='w') as bat_file:
        bat_file.write(f'python {Path("passwordChecker.py").absolute()} file mail {args[1]}\n')
    os.system(f'SchTasks /Create /SC DAILY /TN "passwordChecker cmd task creation test" '
              f'/TR "{bat_file_address}" /ST {args[2]}')
    return "Done"


def main(args):
    if args[0] == "file":
        print("checking saved passwords")
        message_string = file_mode(args)
        if len(args) >= 2:
            if args[1] == "mail":
                send_email(message_string, args[2])
        else:
            print(message_string.replace("<br>", ""))
            #  adjusts the string for terminal output
    elif args[0] == "save":
        save_passwords(args)
    elif args[0] == "task":
        create_task(args)
        print("Task created")
    else:
        for password in args:
            count = pwnd_api_check(password)
            if count:
                print(f'{password} was found {count} times!')
            else:
                print(f'{password} was not found')
        return 'done!'


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
