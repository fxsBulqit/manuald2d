# 📱 Manual D2D Contact Processing System

**Automatically validate emails and send personalized SMS messages to contacts from eCanvasser exports.**

---

## 🎯 What This Does

1. **Reads CSV** from eCanvasser export
2. **Filters contacts** by rating (>= 3)
3. **Validates ALL emails** using ZeroBounce API
4. **Sends SMS** to ALL phone numbers via Twilio
5. **Creates validation report** in CSV format
6. **(Coming Soon) Sends emails** via SendGrid

---

## 📁 Files You Need

```
manuald2d/
├── process_contacts.py    ← RUN THIS FILE
├── config.py             ← Settings & API keys
├── utils.py              ← Helper functions (don't touch)
├── export.csv            ← YOUR DATA GOES HERE
└── README.md             ← You are here
```

---

## ⚡ Quick Start (3 Steps)

### Step 1: Put Your CSV File Here

1. Export contacts from eCanvasser
2. Save/rename it as **`export.csv`**
3. Put it in the `manuald2d` folder

### Step 2: Run The Script

```bash
cd manuald2d
python3 process_contacts.py
```

### Step 3: Check The Results

- **SMS sent!** Check phones for messages
- **Validation results:** Open `email_validation_DDMM.csv` (e.g., `email_validation_2010.csv`)
- **Full log:** Open `processing_log.txt`

---

## 📊 Output Files

| File | What It Contains |
|------|------------------|
| **`email_validation_DDMM.csv`** | All emails with Valid/Invalid status (named with date) |
| **`processing_log.txt`** | Detailed log of everything that happened |

### Example: `email_validation_2010.csv`

```csv
contact_name,email,is_valid
RICHARD KIM,richard@gmail.com,Valid
JANE DOE,bad@fake.com,Invalid
```

**Note:** File is automatically named with the date (day/month). For example, if run on October 20th, it creates `email_validation_2010.csv`

---

## ⚙️ How To Change Settings

Open `config.py` and edit:

### Rating Filter
```python
MIN_RATING = 3  # Only send to contacts rated >= 3
```

### Turn SMS On/Off
```python
SEND_SMS = True   # Set to False to disable SMS
```

### Turn Email On/Off
```python
SEND_EMAILS = False  # Set to True when SendGrid is ready
```

### Dry Run Mode (Test Without Sending)
```python
DRY_RUN = True  # Set to True to test without sending anything
```

---

## 📝 Message Templates

### SMS Message

Edit in `config.py` (line ~34):

```python
def get_sms_message(first_name, organizer_first_name):
    return f"Hey {first_name}, great meeting you today! ..."
```

**Current message:**
> Hey Richard, great meeting you today! We started Bulqit to make it easier for homeowners to get reliable outdoor care with less time, hassle, and cost. If that sounds helpful, you can learn more or sign up here: bulqit.com. -Ferdy

### Email Templates

Edit in `config.py`:
- **Line ~40:** Subject line
- **Line ~47:** Email body (HTML)

---

## 🔑 API Keys (Already Configured)

All API keys are in `config.py`:

| Service | What It Does | Status |
|---------|--------------|--------|
| **ZeroBounce** | Validates emails | ✅ Configured |
| **Twilio** | Sends SMS | ✅ Configured |
| **SendGrid** | Sends emails | ⏳ Waiting on API key |

### To Add SendGrid Later:

1. Get your SendGrid API key
2. Open `config.py`
3. Replace line 11: `SENDGRID_API_KEY = "your_key_here"`
4. Change line 29: `SEND_EMAILS = True`

---

## 🎛️ How It Works

```
┌─────────────────┐
│  export.csv     │  ← Your eCanvasser export
└────────┬────────┘
         ↓
┌─────────────────┐
│ Filter by       │  ← Only rating >= 3
│ Rating          │
└────────┬────────┘
         ↓
    ┌────┴────┐
    ↓         ↓
┌───────┐  ┌───────┐
│Emails │  │Phones │
└───┬───┘  └───┬───┘
    ↓          ↓
┌───────┐  ┌───────┐
│Validate│  │ Send  │
│w/Zero- │  │ SMS   │
│Bounce  │  │Twilio │
└───┬───┘  └───┬───┘
    ↓          ↓
┌───────────────────┐
│ Save Results:     │
│ • validation.csv  │
│ • log.txt         │
└───────────────────┘
```

---

## 📋 CSV Format (eCanvasser Export)

Your CSV must have these columns:

| Column | Example | Required? |
|--------|---------|-----------|
| `First Name` | "RICHARD M U & RACHEL Y" | ✅ Yes |
| `Surname` | "KIM" | ✅ Yes |
| `Rating` | "4" | ✅ Yes |
| `Organizer` | "Ferdy Salmons" | ✅ Yes |
| `Phone_1` to `Phone_5` | "2245004255" | Optional |
| `Email_1` to `Email_3` | "test@gmail.com" | Optional |

**Note:** The script handles multiple phones and emails automatically!

---

## 🔍 Understanding The Output

### Console Output

```
============================================================
👤 Contact: RICHARD M U & RACHEL Y KIM
   First Name: Richard
   Rating: 4
   Organizer: Ferdy Salmons (Ferdy)
   📧 Emails found: 1
   📱 Phones found: 1

   📧 Processing email: richard@gmail.com
      Validation: valid
      ✅ Email is valid

   📱 Processing phone: +12245004255
      ✅ SMS sent successfully
============================================================
```

### What Gets Sent

**SMS to +12245004255:**
```
Hey Richard, great meeting you today! We started Bulqit
to make it easier for homeowners to get reliable outdoor
care with less time, hassle, and cost. If that sounds
helpful, you can learn more or sign up here: bulqit.com.
-Ferdy
```

---

## 🚨 Troubleshooting

### "No emails found"
- Check your CSV has `Email_1`, `Email_2`, or `Email_3` columns
- Make sure email addresses aren't blank

### "No phones found"
- Check your CSV has `Phone_1` through `Phone_5` columns
- Make sure phone numbers aren't blank

### "Skipped - Rating below minimum"
- Contact's rating is less than 3
- Change `MIN_RATING` in `config.py` if needed

### "Twilio error"
- Check API credentials in `config.py`
- Verify Twilio phone number is correct
- Check Twilio account has credits

### "Email validation exception"
- ZeroBounce might be down
- Check internet connection
- API key might be invalid

---

## 💰 Cost Breakdown

| Service | Cost | Free Tier |
|---------|------|-----------|
| **ZeroBounce** | Validates emails | 100 free/month |
| **Twilio SMS** | ~$0.0158/message | $15 trial credit |
| **SendGrid** | Email sending | 100/day free |

**Example:** 100 contacts with rating >= 3:
- Email validation: FREE (under 100)
- SMS: ~$1.58 (100 × $0.0158)
- Emails: FREE (under 100/day)

---

## 🔒 Security Notes

- ✅ API keys stored in `config.py` (not committed to git)
- ✅ All API calls use HTTPS
- ✅ No passwords stored
- ⚠️ Don't share `config.py` with anyone

---

## 📞 Support

### Common Questions

**Q: Can I test without sending real messages?**
A: Yes! Set `DRY_RUN = True` in `config.py`

**Q: How do I change the message?**
A: Edit `get_sms_message()` in `config.py`

**Q: Can I filter by something other than rating?**
A: Yes! Edit `process_contact()` in `process_contacts.py`

**Q: What if someone has multiple phones?**
A: It sends to ALL phones (Phone_1 through Phone_5)

**Q: What if email validation fails?**
A: Invalid emails are logged but NOT sent to

---

## 📌 Quick Reference

### Run the script
```bash
python3 process_contacts.py
```

### Check validation results
```bash
open email_validation_2010.csv  # Replace with today's date
```

### View full log
```bash
cat processing_log.txt
```

### Test mode (no sending)
In `config.py`: `DRY_RUN = True`

---

## ✅ Checklist Before Running

- [ ] `export.csv` is in the `manuald2d` folder
- [ ] CSV has First Name, Surname, Rating, Organizer columns
- [ ] Reviewed message templates in `config.py`
- [ ] Set `MIN_RATING` appropriately
- [ ] API keys are configured
- [ ] (Optional) Set `DRY_RUN = True` for testing

---

**Made with ❤️ for Bulqit D2D campaigns**
