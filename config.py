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
    return f"Hey, I’m Keegan — I live nearby. We left some info at your house earlier. A few of us are trying to get enough homeowners together to group outdoor services like pool, lawn, and pest control so we can all get better pricing and more reliable vendors. I got tired of dealing with the usual hassle, so I built this platform to make it easier. It only takes like 30 secs to register. Once enough neighbors sign up, we’ll go out for bids and you can decide if you wanna jump in (and for which services). 
Can you register? bulqit.com"


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
    return f"Left at your house today"


def get_email_body(first_name, organizer_first_name):
    """
    Generate email body (HTML)
    """
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <p>I dropped off some info at your house earlier today and wanted to tell you more.</p>

        <p>A few of us have been chatting about how nice it’d be if neighbors could team up on home services like lawn care, pools, pest, and windows. It just makes sense when we’re all using the same trusted vendors, and the discounts add up fast.</p>

        <p>That idea turned into a platform my neighbor and I built called Bulqit. It’s a simple way to help neighbors organize, save, and make life easier around the block.</p>

        <p>It only takes about 30 seconds to register. Once enough of us sign up, we’ll go out for bids and you can decide if you want to jump in, and for which services.</p>
        

        <p>You can check it out here: <a href="https://bulqit.com" style="color: #0066cc;">bulqit.com</a></p>

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
