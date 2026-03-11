import re

def check_email(email):

    email = email.strip()

    # space check
    if " " in email:
        return False

    # first letter lowercase check
    if not email[0].islower():
        return False

    # regex email validation
    pattern = r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$'

    return bool(re.match(pattern, email))