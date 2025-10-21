"""
Send emails and SMS to contacts from export.csv
Only processes rows where contacted? = no
Updates contacted? = yes after successful sends
"""

import csv
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import config
from utils import (
    extract_first_name,
    format_phone_number,
    extract_organizer_first_name,
    collect_all_phones,
    collect_all_emails,
    get_rating
)

# Import email/SMS functions from process_contacts
from process_contacts import validate_email, send_email, send_sms, log

def process_and_update_csv(csv_file):
    """Process CSV and update contacted status"""

    log("\n" + "="*60)
    log("🚀 PROCESSING CONTACTS FROM export.csv")
    log("="*60)
    log(f"CSV File: {csv_file}")
    log(f"Dry Run: {config.DRY_RUN}")
    log(f"Send Emails: {config.SEND_EMAILS}")
    log(f"Send SMS: {config.SEND_SMS}")
    log("="*60)

    # Statistics
    stats = {
        'total_rows': 0,
        'already_contacted': 0,
        'processed': 0,
        'emails_valid': 0,
        'emails_invalid': 0,
        'emails_sent': 0,
        'emails_failed': 0,
        'sms_sent': 0,
        'sms_failed': 0,
        'updated_to_yes': 0
    }

    # Read all rows
    rows = []
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
    except FileNotFoundError:
        log(f"❌ ERROR: File not found: {csv_file}")
        return
    except Exception as e:
        log(f"❌ ERROR: {str(e)}")
        return

    stats['total_rows'] = len(rows)

    # Process each row
    for row in rows:
        # Skip if already contacted
        if row.get('contacted?', '').lower() == 'yes':
            stats['already_contacted'] += 1
            continue

        # Extract info
        first_name_raw = row.get('First Name', '')
        surname = row.get('Surname', '')
        organizer = row.get('Organizer', '')

        # Parse names
        first_name = extract_first_name(first_name_raw) if first_name_raw else ''
        organizer_first_name = extract_organizer_first_name(organizer) if organizer else 'Ferdy'

        log(f"\n{'='*60}")
        log(f"👤 Contact: {first_name_raw} {surname}")
        log(f"   First Name: {first_name}")
        log(f"   Organizer: {organizer} ({organizer_first_name})")

        # Collect emails and phones
        emails = collect_all_emails(row)
        phones = collect_all_phones(row)

        log(f"   📧 Emails found: {len(emails)}")
        log(f"   📱 Phones found: {len(phones)}")

        sent_successfully = False

        # Process emails
        for email in emails:
            log(f"\n   📧 Processing email: {email}")

            # Validate email
            is_valid, status = validate_email(email)
            log(f"      Validation: {status}")

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
                    sent_successfully = True
                else:
                    success, result = send_email(email, subject, body, sender_name, sender_email)
                    if success:
                        log(f"      ✅ Email sent successfully from {sender_name} <{sender_email}>")
                        stats['emails_sent'] += 1
                        sent_successfully = True
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
                sent_successfully = True
            else:
                success, result = send_sms(phone, message)
                if success:
                    log(f"      ✅ SMS sent successfully")
                    stats['sms_sent'] += 1
                    sent_successfully = True
                else:
                    log(f"      ❌ SMS failed: {result}")
                    stats['sms_failed'] += 1

        # Mark as contacted if we sent something
        if sent_successfully:
            row['contacted?'] = 'yes'
            stats['updated_to_yes'] += 1
            stats['processed'] += 1

    # Write updated CSV back
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        log(f"\n✅ Updated CSV with contacted status")
    except Exception as e:
        log(f"\n❌ Error updating CSV: {str(e)}")

    # Print summary
    log("\n" + "="*60)
    log("📊 PROCESSING SUMMARY")
    log("="*60)
    log(f"Total rows: {stats['total_rows']}")
    log(f"Already contacted (skipped): {stats['already_contacted']}")
    log(f"Newly processed: {stats['processed']}")
    log(f"Marked as contacted: {stats['updated_to_yes']}")
    log(f"\n📧 EMAIL RESULTS:")
    log(f"   Valid: {stats['emails_valid']}")
    log(f"   Invalid: {stats['emails_invalid']}")
    log(f"   Sent: {stats['emails_sent']}")
    log(f"   Failed: {stats['emails_failed']}")
    log(f"\n📱 SMS RESULTS:")
    log(f"   Sent: {stats['sms_sent']}")
    log(f"   Failed: {stats['sms_failed']}")
    log("="*60)


if __name__ == "__main__":
    # Clear log file
    with open(config.LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("")

    # Process the CSV
    process_and_update_csv("export.csv")

    log(f"\n✅ Done! Full log saved to: {config.LOG_FILE}\n")
