"""
Fetch new interactions from eCanvasser and append to export.csv
Only adds NEW interactions that aren't already in the CSV
"""

import requests
import csv
import os
from datetime import datetime, timedelta

# API Configuration
import os
API_TOKEN = os.environ.get('ECANVASSER_API_TOKEN', "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxMyIsImp0aSI6ImUxNGI2OTQ1M2UwNWZlOGNhY2UzMjdkNzFjYjY2NDkwNmI4MGJhMDgxMjNlMWU0Zjg5N2NhMGRhNGE2Njc2Y2IzZmY0M2EwYzdkMTVjZWIwIiwiaWF0IjoxNzYxMDAwNDAyLjI2ODM0MiwibmJmIjoxNzYxMDAwNDAyLjI2ODM0NCwiZXhwIjoxNzkyNTM2NDAxLjI0NTIzNywic3ViIjoiNTU5ODgzIiwic2NvcGVzIjpbXX0.XbDLr4leAZVsb0teDL0wyvLFQSftTpHTk1lkghQY_WAiGENAjW8eWlPXUzRkhHRf7ulKQFvDGztqgVP3jhEeUP9WZ2Rmhxb_oBqztGulc11LrIQ4C99tmSJWHL9igCZDOm0fQJvc3AW-h91ZTDeHGIfqfFcUo845GZhIEph98GXhjvOwjY3meOsPANVHdrrPLNg4TwG4uw6vTw_I5NzS14LDlLrIxv3xy15FAXzWtlpKIl3_PJipxGAvT3G87Zu7GtbzrkXit1EDlh7aLu1LmG8-5mtzeyte7OYFlvooMWWCFJmCpbm_RiqQ8ROLB0zPkTmg78WqkETCt66u8XxnCXQQ3o79SLNK8ZKGl6gCuv3RrXPHB-ZJfthMetzO8kZI6qIFWsC_UwYeaxMRWflj46NJuEuUTCBJ2HEgPDIgCsrN7q5aWdxyaezn7Npu4QavZzVS4CGDtrTSujM_0M0hwOyGtYO7Dfpsm4E0o248x_sofq2Vt2ZEemnr2kY7BYEmB8NKB_Fk56Gkgsf7jESHIdQOKwiKcxKAPx1l-srULdjI7TDni6si_ACQnEfsHXQ0PrvcDm-GKdOjNNd_4NA2bRK2YLErWHrQV5gSdNYMU_RS1ewdzLtf59wROlIGISesTcNJpaVDvWrFt7CPwEqv2xyWL3RdLgGRCHmFu-4iLLA")
BASE_URL = "https://public-api.ecanvasser.com/v3"
CSV_FILE = "export.csv"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

print("="*80)
print("FETCH NEW INTERACTIONS AND APPEND TO EXPORT.CSV")
print("="*80)

# Step 1: Read existing interaction IDs from CSV
existing_interaction_ids = set()
if os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            interaction_id = row.get('Interaction ID', '')
            if interaction_id:
                existing_interaction_ids.add(interaction_id)
    print(f"📊 Found {len(existing_interaction_ids)} existing interactions in CSV\n")
else:
    print(f"📄 Creating new {CSV_FILE}\n")

# Step 2: Fetch ALL interactions (no date filter, just get everything)
print(f"🔍 Fetching all interactions from eCanvasser...")
interactions_url = f"{BASE_URL}/interaction"
params = {"limit": 1000}

response = requests.get(interactions_url, headers=headers, params=params, timeout=30)
if response.status_code != 200:
    print(f"❌ Failed to fetch interactions: {response.status_code}")
    exit()

interactions_data = response.json()
interactions = interactions_data if isinstance(interactions_data, list) else interactions_data.get('data', [])
print(f"   ✅ Found {len(interactions)} total interactions\n")

# Filter out existing ones
new_interactions = [i for i in interactions if str(i.get('id', '')) not in existing_interaction_ids]
print(f"   🆕 {len(new_interactions)} NEW interactions to add\n")

if len(new_interactions) == 0:
    print("✅ No new interactions to add!")
    exit()

# Step 3: Fetch contact, house, and user data for new interactions
contact_ids = {i.get('contact_id') for i in new_interactions if i.get('contact_id')}
house_ids = {i.get('house_id') for i in new_interactions if i.get('house_id')}
user_ids = {i.get('created_by') for i in new_interactions if i.get('created_by')}

print(f"📡 Fetching {len(contact_ids)} contacts, {len(house_ids)} houses, and {len(user_ids)} users...")

contacts = {}
for contact_id in contact_ids:
    try:
        response = requests.get(f"{BASE_URL}/contact/{contact_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            contacts[contact_id] = data.get('data', data)
    except:
        pass

houses = {}
for house_id in house_ids:
    try:
        response = requests.get(f"{BASE_URL}/house/{house_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            houses[house_id] = data.get('data', data)
    except:
        pass

users = {}
for user_id in user_ids:
    try:
        response = requests.get(f"{BASE_URL}/user/{user_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            user_data = data.get('data', data)
            # Store full name
            first = user_data.get('first_name', '')
            last = user_data.get('last_name', '')
            users[user_id] = f"{first} {last}".strip()
    except:
        pass

print(f"   ✅ Retrieved {len(contacts)} contacts, {len(houses)} houses, and {len(users)} users\n")

# Step 4: Build CSV rows
print("🔨 Building new rows...\n")
new_rows = []

for interaction in new_interactions:
    contact = contacts.get(interaction.get('contact_id'), {})
    house = houses.get(interaction.get('house_id'), {})

    first_name = contact.get('first_name', '')
    surname = contact.get('last_name', '')

    # Extract phones from customFields
    phones = []
    custom_fields = contact.get('customFields', [])
    for field in custom_fields:
        if field.get('name', '').startswith('Phone_'):
            phones.append(field.get('value', ''))

    contact_details = contact.get('contact_details') or {}
    if contact_details.get('mobile'):
        phones.append(contact_details['mobile'])
    if contact_details.get('home'):
        phones.append(contact_details['home'])

    while len(phones) < 5:
        phones.append('')

    # Extract emails
    emails = []
    if contact_details.get('email'):
        emails.append(contact_details['email'])
    for field in custom_fields:
        if field.get('name', '').startswith('Email_'):
            emails.append(field.get('value', ''))
    while len(emails) < 3:
        emails.append('')

    # Extract BB field
    bb = ''
    for field in custom_fields:
        if field.get('name') == 'BB':
            bb = field.get('value', '')
            break

    # Extract status name only (not the whole dict)
    status = interaction.get('status', '')
    if isinstance(status, dict):
        status = status.get('name', '')

    # Get organizer name from users dict
    created_by = interaction.get('created_by', '')
    organizer = users.get(created_by, '')

    new_rows.append({
        'First Name': first_name,
        'Surname': surname,
        'House Unit': house.get('unit', ''),
        'House Name': house.get('house_name', ''),
        'House Number': house.get('house_number', ''),
        'Street Name': house.get('street_name', ''),
        'City': house.get('city', ''),
        'State': house.get('state', ''),
        'Interaction ID': interaction.get('id', ''),
        'Interaction Status': status,
        'Rating': interaction.get('rating', ''),
        'Interaction Date': interaction.get('created_at', ''),
        'Organizer': organizer,
        'Phone_1': phones[0],
        'Phone_2': phones[1],
        'Phone_3': phones[2],
        'Phone_4': phones[3],
        'Phone_5': phones[4],
        'Email_1': emails[0],
        'Email_2': emails[1],
        'Email_3': emails[2],
        'BB': bb,
        'contacted?': 'no'
    })

# Step 5: Append to CSV
fieldnames = [
    'First Name', 'Surname', 'House Unit', 'House Name', 'House Number',
    'Street Name', 'City', 'State', 'Interaction ID', 'Interaction Status',
    'Rating', 'Interaction Date', 'Organizer', 'Phone_1', 'Phone_2',
    'Phone_3', 'Phone_4', 'Phone_5', 'Email_1', 'Email_2', 'Email_3',
    'BB', 'contacted?'
]

file_exists = os.path.exists(CSV_FILE)

with open(CSV_FILE, 'a', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    if not file_exists:
        writer.writeheader()
    writer.writerows(new_rows)

print("="*80)
print("✅ COMPLETE!")
print("="*80)
print(f"Added {len(new_rows)} new rows to {CSV_FILE}")
print(f"Total interactions in CSV: {len(existing_interaction_ids) + len(new_rows)}")
print("="*80)
