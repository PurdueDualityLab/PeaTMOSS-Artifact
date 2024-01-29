import csv
import json

# Read the CSV data
with open('mapping.csv', 'r') as f:
    csv_data = f.read()

# Split the CSV data into lines
lines = csv_data.split('\n')

# Initialize a dictionary to hold the mappings
hf_to_gh_license_mapping = {}

# Parse each line
for line in lines:
    fields = line.split(',')
    print(fields)
    if len(fields) == 4:
        # Extract HF license (last element in the URL) and GH license
        hf_license = fields[3]
        gh_license = fields[1].split('/')[-1]  # Assuming GH license is the last part of the second field
        print(hf_license, gh_license)
        exit()
        # Add to the mapping dictionary
        if hf_license in hf_to_gh_license_mapping:
            hf_to_gh_license_mapping[hf_license].add(gh_license)
        else:
            hf_to_gh_license_mapping[hf_license] = {gh_license}
print(hf_to_gh_license_mapping)

hf_to_gh_license_mapping_for_json = {k: list(v) for k, v in hf_to_gh_license_mapping.items()}

