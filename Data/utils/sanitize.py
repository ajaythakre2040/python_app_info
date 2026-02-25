import re
from rest_framework.exceptions import ValidationError

HTML_TAG_RE = re.compile(r'<[^>]+>')  

UNSAFE_CHARS_RE = re.compile(r'[<>+&"]')

def no_html_validator(value):
    if not value:
        return value

    if re.search(HTML_TAG_RE, value):
        raise ValidationError("HTML tags are not allowed.")

    if re.search(UNSAFE_CHARS_RE, value):
        raise ValidationError("Input contains unsafe characters like <, >, +, &, \" ")

    return value
