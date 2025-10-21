"""
Utility functions for contact processing
"""

import re

def extract_first_name(full_name):
    """
    Extract first name from complex name strings

    Examples:
        "RICHARD M U & RACHEL Y" -> "Richard"
        "John Doe" -> "John"
        "MARY-JANE" -> "Mary-Jane"
    """
    if not full_name or not isinstance(full_name, str):
        return "Friend"

    # Clean up the name
    name = full_name.strip()

    # Split by common separators and take first part
    # Split by & or / to handle multiple names
    if '&' in name:
        name = name.split('&')[0].strip()
    if '/' in name:
        name = name.split('/')[0].strip()

    # Take first word
    first_word = name.split()[0] if name.split() else name

    # Remove special characters but keep hyphens
    first_word = re.sub(r'[^a-zA-Z\-]', '', first_word)

    # Title case
    first_word = first_word.title()

    return first_word if first_word else "Friend"


def format_phone_number(phone):
    """
    Format phone number to E.164 format (+1XXXXXXXXXX)

    Examples:
        "2245004255" -> "+12245004255"
        "(224) 500-4255" -> "+12245004255"
        "+1-224-500-4255" -> "+12245004255"
    """
    if not phone or not isinstance(phone, str):
        return None

    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)

    # If it's empty after cleaning, return None
    if not digits:
        return None

    # If it's 10 digits, add +1 (US)
    if len(digits) == 10:
        return f"+1{digits}"

    # If it's 11 digits and starts with 1, add +
    if len(digits) == 11 and digits[0] == '1':
        return f"+{digits}"

    # If it already has proper length, return as is with +
    if len(digits) >= 10:
        return f"+{digits}"

    # Too short, invalid
    return None


def extract_organizer_first_name(organizer_full_name):
    """
    Extract organizer's first name from full name

    Examples:
        "Ferdy Salmons" -> "Ferdy"
        "Tom Smith" -> "Tom"
    """
    if not organizer_full_name or not isinstance(organizer_full_name, str):
        return "The Team"

    first_name = organizer_full_name.split()[0] if organizer_full_name.split() else organizer_full_name
    return first_name.strip().title()


def collect_all_phones(row):
    """
    Collect all phone numbers from a contact row
    Returns list of formatted phone numbers
    """
    phones = []

    # Check Phone_1 through Phone_5
    for i in range(1, 6):
        phone_col = f'Phone_{i}'
        if phone_col in row and row[phone_col]:
            formatted = format_phone_number(str(row[phone_col]))
            if formatted and formatted not in phones:  # Avoid duplicates
                phones.append(formatted)

    return phones


def collect_all_emails(row):
    """
    Collect all email addresses from a contact row
    Returns list of email addresses
    """
    emails = []

    # Check Email_1 through Email_3
    for i in range(1, 4):
        email_col = f'Email_{i}'
        if email_col in row and row[email_col]:
            email = str(row[email_col]).strip().lower()
            if email and '@' in email and email not in emails:  # Basic validation + avoid duplicates
                emails.append(email)

    return emails


def get_rating(row):
    """
    Extract rating from row, return as integer
    Returns 0 if no rating or invalid
    """
    try:
        if 'Rating' in row and row['Rating']:
            return int(row['Rating'])
    except (ValueError, TypeError):
        pass

    return 0
