"""
Main Contact Processing Script
Reads eCanvasser CSV export and sends personalized emails + SMS
"""

import csv
import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime

# Import our modules
import config
from utils import (
    extract_first_name,
    format_phone_number,
    extract_organizer_first_name,
    collect_all_phones,
    collect_all_emails,
    get_rating
)


# ============================================
# EMAIL VALIDATION (ZeroBounce)
# ============================================

def validate_email(email):
    """Validate email using ZeroBounce API"""
    url = "https://api.zerobounce.net/v2/validate"

    params = {
        "api_key": config.ZEROBOUNCE_API_KEY,
        "email": email,
        "ip_address": ""
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')

            # Valid statuses to send to
            return status == 'valid', status
        else:
            return False, "api_error"

    except Exception as e:
        log(f"   ❌ Email validation exception: {str(e)}")
        return False, "exception"


# ============================================
# EMAIL SENDING (SendGrid)
# ============================================

def send_email(to_email, subject, html_content, sender_name=None, sender_email=None):
    """Send email using SendGrid API"""

    if not config.SEND_EMAILS:
        log(f"   ⏭️  Email sending disabled (SEND_EMAILS=False)")
        return False, "disabled"

    if config.SENDGRID_API_KEY == "YOUR_SENDGRID_API_KEY_HERE":
        log(f"   ⏭️  SendGrid API key not configured")
        return False, "no_api_key"

    url = "https://api.sendgrid.com/v3/mail/send"

    headers = {
        "Authorization": f"Bearer {config.SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    # Build from field with optional name and email
    from_field = {"email": sender_email if sender_email else config.SENDGRID_FROM_EMAIL}
    if sender_name:
        from_field["name"] = sender_name

    payload = {
        "personalizations": [{"to": [{"email": to_email}], "bcc": [{"email": "sales@bulqit.com"}]}],
        "from": from_field,
        "subject": subject,
        "content": [{"type": "text/html", "value": html_content}]
    }

    # Retry logic: try up to 3 times
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 202:  # SendGrid returns 202 for success
                if attempt > 1:
                    log(f"   ✅ Email sent on retry attempt {attempt}")
                return True, "sent"
            else:
                log(f"   ❌ SendGrid error (attempt {attempt}): {response.text}")
                if attempt < max_retries:
                    log(f"   🔄 Retrying...")
                    continue
                return False, "api_error"

        except Exception as e:
            log(f"   ❌ Email sending exception (attempt {attempt}): {str(e)}")
            if attempt < max_retries:
                log(f"   🔄 Retrying...")
                continue
            return False, "exception"

    return False, "max_retries_exceeded"


# ============================================
# SMS SENDING (Twilio)
# ============================================

def send_sms(to_phone, message):
    """Send SMS using Twilio API"""

    if not config.SEND_SMS:
        log(f"   ⏭️  SMS sending disabled (SEND_SMS=False)")
        return False, "disabled"

    url = f"https://api.twilio.com/2010-04-01/Accounts/{config.TWILIO_ACCOUNT_SID}/Messages.json"

    data = {
        "To": to_phone,
        "From": config.TWILIO_FROM_PHONE,
        "Body": message
    }

    try:
        response = requests.post(
            url,
            data=data,
            auth=HTTPBasicAuth(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN),
            timeout=10
        )

        if response.status_code == 201:  # Twilio returns 201 for success
            return True, "sent"
        else:
            log(f"   ❌ Twilio error: {response.text}")
            return False, "api_error"

    except Exception as e:
        log(f"   ❌ SMS sending exception: {str(e)}")
        return False, "exception"


# ============================================
# LOGGING
# ============================================

def log(message, also_to_file=True):
    """Print and optionally write to log file"""
    if config.VERBOSE:
        print(message)

    if also_to_file:
        with open(config.LOG_FILE, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")


# ============================================
# MAIN PROCESSING
# ============================================

def process_contact(row, stats, validation_results):
    """Process a single contact from CSV"""

    # Extract basic info
    first_name_raw = row.get('First Name', '')
    surname = row.get('Surname', '')
    rating = get_rating(row)
    organizer = row.get('Organizer', '')

    # Parse names
    first_name = extract_first_name(first_name_raw)
    organizer_first_name = extract_organizer_first_name(organizer)

    log(f"\n{'='*60}")
    log(f"👤 Contact: {first_name_raw} {surname}")
    log(f"   First Name: {first_name}")
    log(f"   Rating: {rating}")
    log(f"   Organizer: {organizer} ({organizer_first_name})")

    # Rating check disabled - process ALL contacts regardless of rating
    # if rating < config.MIN_RATING:
    #     log(f"   ⏭️  SKIPPED - Rating {rating} is below minimum {config.MIN_RATING}")
    #     stats['skipped_low_rating'] += 1
    #     return

    stats['processed'] += 1

    # Collect all contact methods
    emails = collect_all_emails(row)
    phones = collect_all_phones(row)

    log(f"   📧 Emails found: {len(emails)}")
    log(f"   📱 Phones found: {len(phones)}")

    # Process emails
    for email in emails:
        log(f"\n   📧 Processing email: {email}")

        # Validate email
        is_valid, status = validate_email(email)
        log(f"      Validation: {status}")

        # Record validation result
        validation_results.append({
            'contact_name': f"{first_name_raw} {surname}",
            'email': email,
            'is_valid': 'Valid' if is_valid else 'Invalid'
        })

        if is_valid:
            stats['emails_valid'] += 1

            # Generate email content
            subject = config.get_email_subject(first_name)
            body = config.get_email_body(first_name, organizer_first_name)
            sender_name = config.get_sender_name(organizer_first_name)
            sender_email = config.get_sender_email(organizer_first_name)

            # Send email
            if config.DRY_RUN:
                log(f"      🔍 DRY RUN - Would send email")
                log(f"         Subject: {subject}")
                log(f"         From: {sender_name} <{sender_email}>")
            else:
                success, result = send_email(email, subject, body, sender_name, sender_email)
                if success:
                    log(f"      ✅ Email sent successfully from {sender_name} <{sender_email}>")
                    stats['emails_sent'] += 1
                else:
                    log(f"      ❌ Email failed: {result}")
                    stats['emails_failed'] += 1
        else:
            log(f"      ❌ Email invalid, not sending")
            stats['emails_invalid'] += 1

    # Process phones
    for phone in phones:
        log(f"\n   📱 Processing phone: {phone}")

        # Generate SMS message
        message = config.get_sms_message(first_name, organizer_first_name)

        # Send SMS
        if config.DRY_RUN:
            log(f"      🔍 DRY RUN - Would send SMS")
            log(f"         Message: {message[:50]}...")
        else:
            success, result = send_sms(phone, message)
            if success:
                log(f"      ✅ SMS sent successfully")
                stats['sms_sent'] += 1
            else:
                log(f"      ❌ SMS failed: {result}")
                stats['sms_failed'] += 1


def process_csv(csv_file):
    """Process entire CSV file"""

    log("\n" + "="*60)
    log("🚀 STARTING CONTACT PROCESSING")
    log("="*60)
    log(f"CSV File: {csv_file}")
    log(f"Min Rating: {config.MIN_RATING}")
    log(f"Dry Run: {config.DRY_RUN}")
    log(f"Send Emails: {config.SEND_EMAILS}")
    log(f"Send SMS: {config.SEND_SMS}")
    log("="*60)

    # Statistics
    stats = {
        'total_rows': 0,
        'processed': 0,
        'skipped_low_rating': 0,
        'emails_valid': 0,
        'emails_invalid': 0,
        'emails_sent': 0,
        'emails_failed': 0,
        'sms_sent': 0,
        'sms_failed': 0
    }

    # Email validation results for CSV output
    validation_results = []

    # Read and process CSV
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
            reader = csv.DictReader(f)

            for row in reader:
                stats['total_rows'] += 1
                process_contact(row, stats, validation_results)

    except FileNotFoundError:
        log(f"❌ ERROR: File not found: {csv_file}")
        return
    except Exception as e:
        log(f"❌ ERROR: {str(e)}")
        return

    # Write email validation results to CSV
    if validation_results:
        try:
            # Generate filename with current date (DDMM format)
            from datetime import datetime
            date_str = datetime.now().strftime("%d%m")
            output_filename = f"email_validation_{date_str}.csv"

            with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['contact_name', 'email', 'is_valid']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for result in validation_results:
                    writer.writerow(result)

            log(f"\n✅ Email validation results saved to: {output_filename}")
        except Exception as e:
            log(f"\n❌ Error saving validation results: {str(e)}")

    # Print summary
    log("\n" + "="*60)
    log("📊 PROCESSING SUMMARY")
    log("="*60)
    log(f"Total rows: {stats['total_rows']}")
    log(f"Processed: {stats['processed']}")
    log(f"Skipped (low rating): {stats['skipped_low_rating']}")
    log(f"\n📧 EMAIL RESULTS:")
    log(f"   Valid: {stats['emails_valid']}")
    log(f"   Invalid: {stats['emails_invalid']}")
    log(f"   Sent: {stats['emails_sent']}")
    log(f"   Failed: {stats['emails_failed']}")
    log(f"\n📱 SMS RESULTS:")
    log(f"   Sent: {stats['sms_sent']}")
    log(f"   Failed: {stats['sms_failed']}")
    log("="*60)


# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    # Clear log file
    with open(config.LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("")

    # Process the CSV
    process_csv("export.csv")

    log(f"\n✅ Done! Full log saved to: {config.LOG_FILE}\n")
