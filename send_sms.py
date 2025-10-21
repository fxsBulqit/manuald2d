"""
Simple SMS sender - sends a text message via Twilio
"""

import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import os

# Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_FROM_PHONE = os.environ.get('TWILIO_FROM_PHONE', '+13103614543')

# Recipient
TO_PHONE = "+12245004255"

def send_sms():
    """Send SMS via Twilio"""

    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"

    # Message with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"Test message from GitHub Actions at {timestamp}"

    data = {
        "To": TO_PHONE,
        "From": TWILIO_FROM_PHONE,
        "Body": message
    }

    try:
        response = requests.post(
            url,
            data=data,
            auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=10
        )

        if response.status_code == 201:
            print(f"✅ SMS sent successfully at {timestamp}")
            print(f"   To: {TO_PHONE}")
            print(f"   Message: {message}")
            return True
        else:
            print(f"❌ Failed to send SMS: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    send_sms()
