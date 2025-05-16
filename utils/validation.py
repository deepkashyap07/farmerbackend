from email_validator import validate_email as ve, EmailNotValidError

def validate_email(email):
    try:
        ve(email)
        return True
    except EmailNotValidError:
        return False
