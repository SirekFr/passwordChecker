import requests
import hashlib
import sys
import smtplib
from email.message import EmailMessage
from string import Template
from pathlib import Path  # os.path


def send_email(message):
    html = Template(Path('index.html').read_text())

    email = EmailMessage()
    email['from'] = 'passwordChecker'
    email['to'] = ''
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
    sha1password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    hashed = [sha1password[:5], sha1password[5:]]
    return hashed


def pwnd_api_check(password):
    hashed = generate_hash(password)
    response = request_api_data(hashed[0])
    return get_password_leaks_count(response, hashed[1])


def file_mode(args):
    try:
        with open('saved.txt', mode='r') as saved_file:
            lines = saved_file.readlines()
            message_string = ""
            for line in lines:
                saved_hash = line.rsplit(' ')
                response = request_api_data(saved_hash[0])
                leaks_count = get_password_leaks_count(response, saved_hash[1])

                first_two_letters = saved_hash[2].replace('\n', '')
                message_string += (f"Password starting with {first_two_letters}, "
                                   f"has been leaked {leaks_count} times.\n <br>")
        if len(args) == 2:
            if args[1] == "mail":
                send_email(message_string)
    except FileNotFoundError as err:
        print('file does not exist')
        raise err


def save_passwords(args):
    try:
        with open('saved.txt', mode='a') as saved_file:
            for password in args[1:]:
                hashed = generate_hash(password)
                first_two = password[:2]
                saved_file.write(f'{hashed[0]} {hashed[1]} {first_two}\n')
    except FileNotFoundError as err:
        print('file does not exist')
        raise err


def main(args):
    if args[0] == "file":
        print("checking saved passwords")
        file_mode(args)
    elif args[0] == "save":
        save_passwords(args)
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
