# 🚀 D2D Contact Automation Workflow

Complete automated system for processing eCanvasser contacts and sending emails/SMS.

---

## 📁 Files

| File | Purpose |
|------|---------|
| `fetch_and_append.py` | Fetches new interactions from eCanvasser API and appends to export.csv |
| `send_to_contacts.py` | Sends emails/SMS to contacts where contacted? = no, then marks them as yes |
| `export.csv` | Main database of all contacts (grows over time) |
| `config.py` | Configuration & API keys |
| `utils.py` | Helper functions |
| `process_contacts.py` | Email/SMS sending functions |

---

## 🔄 Complete Workflow

### Step 1: Fetch New Contacts
```bash
python3 fetch_and_append.py
```

**What it does:**
- Fetches interactions from last 24 hours via eCanvasser API
- Gets contact details (names, phones, emails)
- Gets house details (addresses)
- **Appends** only NEW interactions to export.csv
- All new rows have `contacted? = no`

### Step 2: Send to Contacts
```bash
python3 send_to_contacts.py
```

**What it does:**
- Reads export.csv
- **Skips rows where contacted? = yes**
- For each row where contacted? = no:
  - Validates emails via ZeroBounce
  - Sends emails via SendGrid (if valid)
  - Sends SMS via Twilio
- **Updates contacted? = yes** after successful sends
- Never contacts the same person twice!

---

## ⚙️ Configuration

Edit `config.py` to change:

```python
# Test mode (doesn't actually send)
DRY_RUN = False  # Set to True for testing

# Enable/disable channels
SEND_EMAILS = True
SEND_SMS = True

# Customize messages
def get_sms_message(first_name, organizer_first_name):
    return f"Hey {first_name}..."

def get_email_body(first_name, organizer_first_name):
    return f"<html>Hey {first_name}...</html>"
```

---

## 📊 Data Flow

```
eCanvasser API
      ↓
fetch_and_append.py
      ↓
export.csv (contacted? = no)
      ↓
send_to_contacts.py
      ↓
  ✉️  Emails sent
  📱 SMS sent
      ↓
export.csv (contacted? = yes)
      ↓
NEVER CONTACTED AGAIN!
```

---

## 🎯 Daily Routine

Run both scripts daily:

```bash
# 1. Fetch new contacts from eCanvasser
python3 fetch_and_append.py

# 2. Send to new contacts
python3 send_to_contacts.py
```

**That's it!** The system:
- ✅ Automatically tracks who's been contacted
- ✅ Never sends duplicates
- ✅ Grows export.csv over time
- ✅ Validates emails before sending
- ✅ Logs everything

---

## 📝 Output Files

| File | What It Contains |
|------|------------------|
| `export.csv` | Master contact database |
| `processing_log.txt` | Detailed logs of all operations |
| `email_validation_DDMM.csv` | Email validation results (optional) |

---

## 🔐 Security

- API keys are in `config.py` (not in git)
- All files in `.gitignore` are kept private
- HTTPS for all API calls

---

## 💡 Tips

- **Run fetch_and_append.py multiple times** - it only adds NEW interactions
- **contacted? = yes is permanent** - once marked, never contacted again
- **Check processing_log.txt** for detailed results
- **Use DRY_RUN = True** to test without sending

---

**Built with ❤️ for Bulqit D2D campaigns**
