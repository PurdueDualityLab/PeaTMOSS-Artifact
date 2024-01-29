import pandas as pd
import re
import json
import sys
import csv

otherNum = 250

# file paths for hf license -> gh license relations
hf_license_to_gh_repo_csv = "mapping.csv"
gh_repo_url_column = 0
hf_license_column = 3

gh_repo_to_gh_license_json = "all_gh_licenses.json"

# Load data from hf_gh_licenses.json
df = pd.read_csv(hf_license_to_gh_repo_csv, header=None)

# Load data from the GH JSON file as text
with open(gh_repo_to_gh_license_json, 'r', encoding='utf-8') as f:
    GH_data = f.read()

# Attempt to load the JSON data as a Python dictionary
try:
    GH_license_dict = json.loads(GH_data)
except json.JSONDecodeError as e:
    # If decoding fails, set the value to None
    print(f"Error decoding {gh_repo_to_gh_license_json}: {e}")
    exit()
    
# known aliases in analyzed data
aliases = {
    "bsd-new": "bsd-3-clause",
    "bsd-modified": "bsd-3-clause",
    "bsd-simplified": "bsd-2-clause",
    'openrail++':'openrail',
}
    
def extract_repo_name(url):
    # Unescape forward slashes
    url = url.replace(r"\/", "/")
    
    # Use regular expression to extract repo name
    match = re.search(r"github\.com[\/:](.+\/.+?)(?:\.git)?$", url)
    
    if match:
        return match.group(1)
    else:
        return None
    
    
hf_license_count = {}    
gh_license_count = {}    
for cnt, row in df.iterrows():
        # display count
    counter_str = f"\rProcessed {cnt}/{df.shape[0]-1} relations"
    sys.stdout.write(counter_str)
    sys.stdout.flush()
    
    # get HF and GH licenses
    if(not pd.notna(row[hf_license_column])):
        hf_license = "no license"
    else:
        hf_license = row[hf_license_column].lower()
    gh_repo_name = extract_repo_name(row[gh_repo_url_column])
    gh_license = GH_license_dict[gh_repo_name]
    
    # process current GH and HF Licenses 
    # to filter out 'other', process 'no license', 
    # and process found aliases
    if type(gh_license) is type(None):
        gh_license = ["no license"]
    if gh_license is None or not gh_license:
        for l in gh_license:
            if pd.notna(l):
                gh_license = l
    if not pd.notna(hf_license) or hf_license == "unlicense":
        hf_license = "no license"
        
    if hf_license=="other" or hf_license=='unknown' or hf_license=='unknown-license-reference' or hf_license=='warranty-disclaimer' or hf_license=='generic-cla' or hf_license=='commercial-license' or hf_license=='other-permissive' or hf_license=='other-copyleft':
        hf_license = "other"
    if hf_license in aliases.keys():
        hf_license = aliases[hf_license]
    
    if(hf_license not in hf_license_count.keys()):
        hf_license_count[hf_license] = 1
    else:
        hf_license_count[hf_license] += 1

    for l in gh_license:
        # process current GH license to filter out 'other,
        # process 'no license', and process found aliases
        if(l=="unlicense"):
            l = "no license"
        if(l=="other" or l=='unknown' or l=='unknown-license-reference' or l=='warranty-disclaimer' or l=='generic-cla' or l=='commercial-license' or l=='other-permissive' or l=='other-copyleft'):
            l = "other"
        if(l in aliases.keys()):
            l = aliases[l]
        
        if(l not in gh_license_count.keys()):
            gh_license_count[l] = 1
        else:
            gh_license_count[l] += 1
            
hf_other = []
gh_other = []

for l in hf_license_count.keys():
    if(hf_license_count[l] <= otherNum):
        hf_other.append(l)
        
        
for l in gh_license_count.keys():
    if(gh_license_count[l] <= otherNum):
        gh_other.append(l)
        

with open('hf_other.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(hf_other)
with open('gh_other.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(gh_other)