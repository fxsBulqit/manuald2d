"""
Merge phone data from pr.csv into export.csv
Matches on Address (House Number + Street Name)
"""

import csv

def merge_phone_data():
    # Read pr.csv and create address -> phone mapping
    phone_lookup = {}

    with open('pr.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            address = row.get('Address', '').strip()
            if not address or 'PropertyRadar' in address:
                continue

            phone_lookup[address] = {
                'Primary Phone1': row.get('Primary Phone1', '').strip(),
                'Primary Mobile Phone1': row.get('Primary Mobile Phone1', '').strip(),
                'Secondary Phone1': row.get('Secondary Phone1', '').strip(),
                'Secondary Mobile Phone1': row.get('Secondary Mobile Phone1', '').strip()
            }

    print(f"📱 Loaded {len(phone_lookup)} addresses with phone data from pr.csv")

    # Read export.csv
    output_rows = []
    matches = 0
    no_matches = 0

    with open('export.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            # Build address from export.csv
            house_number = row.get('House Number', '').strip()
            street_name = row.get('Street Name', '').strip()

            if house_number and street_name:
                address = f"{house_number} {street_name}"

                # Look up phone data
                if address in phone_lookup:
                    phones = phone_lookup[address]

                    # Collect all unique phones
                    all_phones = []
                    for phone_type in ['Primary Phone1', 'Primary Mobile Phone1', 'Secondary Phone1', 'Secondary Mobile Phone1']:
                        phone = phones[phone_type]
                        if phone and phone not in all_phones:
                            all_phones.append(phone)

                    # Populate Phone_1 through Phone_5
                    for i, phone in enumerate(all_phones[:5], 1):
                        row[f'Phone_{i}'] = phone

                    matches += 1
                else:
                    no_matches += 1

            output_rows.append(row)

    # Write updated export.csv
    with open('export.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"✅ Updated export.csv")
    print(f"   Matched: {matches} addresses with phone data")
    print(f"   No match: {no_matches} addresses")
    print(f"   Total rows: {len(output_rows)}")

if __name__ == "__main__":
    merge_phone_data()
