"""
Configuration file for contact processing system
"""
import os

# ============================================
# API CREDENTIALS
# ============================================

# ZeroBounce (Email Validation)
ZEROBOUNCE_API_KEY = os.environ.get('ZEROBOUNCE_API_KEY', "YOUR_ZEROBOUNCE_API_KEY")

# SendGrid (Email Sending)
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', "YOUR_SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = "fxs@bulqit.com"

# Twilio (SMS Sending)
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', "YOUR_TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', "YOUR_TWILIO_AUTH_TOKEN")
TWILIO_FROM_PHONE = "+13103614543"

# ============================================
# PROCESSING RULES
# ============================================

# Minimum rating to send messages (>= this value)
MIN_RATING = 3

# Whether to actually send messages (False = dry run, just validate and log)
DRY_RUN = False

# Whether to send emails (set to False to skip email sending)
SEND_EMAILS = True

# Whether to send SMS
SEND_SMS = True

# ============================================
# MESSAGE TEMPLATES
# ============================================

def get_sms_message(first_name, organizer_first_name):
    """
    Generate SMS message with personalization
    """
    return f"Hey there, we just dropped off some material about grouping our neighbors together to lower home services. If you can register, it takes 30 seconds and there's no charge or commitment until after we get bids. Thanks for supporting the neighborhood. Here's the link, www.bulqit.com. -{organizer_first_name}"


def get_sender_name(organizer_first_name):
    """
    Map organizer first name to full sender name
    """
    organizer_map = {
        'Keegan': 'Keegan Bonebrake',
        'Tom': 'Tom Vranas',
        'Ferdy': 'Ferdy Salmons'
    }

    # Default to organizer's first name if not in map
    return organizer_map.get(organizer_first_name, organizer_first_name)


def get_sender_email(organizer_first_name):
    """
    Map organizer first name to sender email address
    """
    email_map = {
        'Keegan': 'kjb@bulqit.com',
        'Tom': 'tjv@bulqit.com',
        'Ferdy': 'fxs@bulqit.com'
    }

    # Default to fxs@bulqit.com if not in map
    return email_map.get(organizer_first_name, 'fxs@bulqit.com')


def get_email_subject(first_name):
    """
    Generate email subject line
    """
    return f"Great meeting you today!"


def get_email_body(first_name, organizer_first_name):
    """
    Generate email body (HTML)
    """
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <p>Hey there,</p>

        <p>It was great meeting you today - we're really looking forward to being a part of the neighborhood!</p>

        <p>We started Bulqit to make it easier for homeowners to get reliable outdoor care - the same trusted local vendors, but with less time, hassle, and cost. We are very excited for it, and glad you are too!</p>

        <p>If that sounds helpful, you can learn more or sign up here: <a href="https://bulqit.com" style="color: #0066cc;">bulqit.com</a></p>

        <p>Best,<br>
        {organizer_first_name}</p>
    </body>
    </html>
    """

# ============================================
# LOGGING & OUTPUT
# ============================================

# Log file location
LOG_FILE = "processing_log.txt"

# CSV output for email validation results (will be named with date)
# Format: email_validation_DDMM.csv (e.g., email_validation_2010.csv)
VALIDATION_OUTPUT_CSV = None  # Generated dynamically with date

# Whether to print detailed output
VERBOSE = True
