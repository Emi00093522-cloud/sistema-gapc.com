import re

def validate_email(email):
    if not email:
        return True
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    if not phone:
        return True
    cleaned = phone.replace('-', '')
    return cleaned.isdigit() and len(cleaned) == 8

def validate_dui(dui):
    if not dui:
        return True
    if len(dui) == 10 and dui[8] == '-':
        return dui[:8].isdigit() and dui[9:].isdigit()
    return False
