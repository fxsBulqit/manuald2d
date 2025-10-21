import csv

# The 8 contacts to reset (using Interaction IDs from the grep results)
contacts_to_reset = [
    ('MATTHEW J', 'HERMES'),
    ('CECILY C', 'BURTON'),
    ('ALAN & NANCY', 'SACHS'),
    ('ERIC & DEBORAH', 'LEVINRAD'),
    ('DAVID & MARCELLE', 'ROTHMAN'),
    ('MARILYN', 'AZAR'),
    ('SHMUEL', 'ASHKENASI'),
    ('DINESH', 'CHHETRI')
]

# Read the CSV
rows = []
with open('export.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        rows.append(row)

# Reset the contacted status for these 8
reset_count = 0
for row in rows:
    first_name = row.get('First Name', '').strip()
    surname = row.get('Surname', '').strip()

    for contact_first, contact_last in contacts_to_reset:
        if first_name == contact_first and surname == contact_last:
            if row.get('contacted?', '').lower() == 'yes':
                row['contacted?'] = 'no'
                reset_count += 1
                print(f"Reset: {first_name} {surname} (Interaction {row.get('Interaction ID')})")

# Write back to CSV
with open('export.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\n✅ Reset {reset_count} contacts to 'no'")
