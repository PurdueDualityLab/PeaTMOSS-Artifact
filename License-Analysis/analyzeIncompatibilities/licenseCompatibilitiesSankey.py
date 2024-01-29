import pandas as pd
import plotly.graph_objects as go
import re
import json
import sys

# licenses in sankey 'other' due to being less than the filter count
df = pd.read_csv('hf_other.csv', header=None)
hf_other = df.values.tolist()[0]
df = pd.read_csv('gh_other.csv', header=None)
gh_other = df.values.tolist()[0]

# file paths for hf license -> gh license relations
hf_license_to_gh_repo_csv = "mapping.csv"
gh_repo_url_column = 0
hf_repo_url_column = 2
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
    'openrail++': 'openrail',    
    'gpl-2.0': 'gpl-2.0-only',
    'gpl-3.0': 'gpl-3.0-only',
    'gpl-3.0-plus': 'gpl-3.0-or-later',
    'agpl-3.0': 'agpl-3.0-only',
    'lgpl-3.0': 'lgpl-3.0-only',
    'lgpl-3.0-plus': 'lgpl-3.0-or-later',
    'lgpl-2.1': 'lgpl-2.1-only',
    
}

# process Linux Foundation Compatabilities Table
relationalTable = pd.read_excel("Linux-Foundation-OSS-License-Compatibility.xlsx", index_col=0)

known_HF_licenses = list(relationalTable.columns)
known_GH_licenses = list(relationalTable.index)

# function to get the compatibility of the licenses
# returns int:
#   1 - compatible
#   0 - incompatible
#  -1 - unknown
val_dict = {
    "?": -1,
    "yes": 1,
    "no": 0
}
def get_relationship(original, derivative):
    if((original not in known_HF_licenses) or (derivative not in known_GH_licenses)):
        return -1
    if(original == derivative):
        return 1
    
    val = relationalTable.loc[derivative, original] # 'RowLabel', 'ColumnLabel'
    
    return val_dict[val]

# Create a function to extract the repository name from a GitHub URL so all_gh_licenses.json can be queried with {username}/{repo}
def extract_repo_name(url):
    # Unescape forward slashes
    url = url.replace(r"\/", "/")
    
    # Use regular expression to extract repo name
    match = re.search(r"github\.com[\/:](.+\/.+?)(?:\.git)?$", url)
    
    if match:
        return match.group(1)
    else:
        return None


others = ["other", 'unknown', 'unknown-license-reference', 'warranty-disclaimer', 'generic-cla', 'commercial-license', 'other-permissive', 'other-copyleft']
def process_license(license):
    if type(license) is type(None) or license == "unlicense":
        return "no license"
    if license in others:
        return "other"
    if license in aliases.keys():
        return aliases[license]
    return license

SankeyRelations = {}
""" Sankey Relations
{
    hf_license1: {
        gh_license1: {
            count: number
            color: rgba
        },
        ...
    },
    ...
}
"""
opacity = 0.3
red =  f"rgba(255,0,0,{1})"
blue = f"rgba(0,0,255,{opacity})"
grey = f"rgba(110,110,110,{opacity})"
allHFPTMS = set()
allGHRepos = set()
analyzedHFPTMS = set()
analyzedGHRepos = set()
unanalyzedHFlicenses = set()
unanalyzedGHlicenses = set()
totalRelationsCNT = 0
identicalRelations = 0
skippedNum = 0
numCompatible = 0
numIncompatible = 0
numUnkown = 0
for cnt, row in df.iterrows():
    # display count
    counter_str = f"\rProcessed {cnt}/{df.shape[0]-1} relations"
    sys.stdout.write(counter_str)
    sys.stdout.flush()
    
    # track the PTMs and Repos which are looked at
    allHFPTMS.add(row[hf_repo_url_column])
    allGHRepos.add(row[gh_repo_url_column])
    
    # get HF and GH licenses
    if(not pd.notna(row[hf_license_column])):
        hf_license = "no license"
    else:
        hf_license = row[hf_license_column].lower()
    gh_repo_name = extract_repo_name(row[gh_repo_url_column])
    gh_licenses = GH_license_dict[gh_repo_name]
    if type(gh_licenses) is type(None):
        gh_licenses = ["no license"]
    if(len(gh_licenses) > 1): # only analyzing “one GH repo one license”
        skippedNum += 1
        continue
    hf_license = process_license(hf_license)
    
    # check if HF license is filtered to other by the set other count
    # to reduce the clutter in the Sankey
    hf_license_alt = hf_license
    if(hf_license in hf_other or hf_license not in known_HF_licenses):
        hf_license_alt = "other"
    
    # process data for Sankey Diagram
    # first need to see if the current HF license has been added as a source yet
    if(hf_license_alt not in SankeyRelations.keys()):
        SankeyRelations[hf_license_alt] = dict()
    
    # only ever 1 license in this context here to
    # allow an easy switch to analyze multi license repose
    for gh_license in gh_licenses:
        gh_license = process_license(gh_license)
        if(gh_license == hf_license):
            identicalRelations += 1
        color = blue
        
        # do not know relation of "other"
        if(hf_license == "other" or gh_license == "other"):
            color = grey
            
        # see if the relation is known by the Linux Foundation Table
        if(gh_license not in known_GH_licenses): 
            color = grey
            unanalyzedGHlicenses.add(gh_license)
        if(hf_license not in known_HF_licenses): 
            color = grey
            unanalyzedHFlicenses.add(hf_license)
            
        relationship = get_relationship(hf_license, gh_license)
        totalRelationsCNT += 1
        if(relationship == 0):
            numIncompatible += 1
            color = red
        elif(relationship == -1):
            numUnkown += 1
            color = grey
        else:
            numCompatible += 1
            color = blue
        
        # check if HF license is filtered to other by the set other count
        # to reduce the clutter in the Sankey
        gh_license_alt = gh_license
        if(gh_license in gh_other or (gh_license not in known_GH_licenses and gh_license != "no license")):
            gh_license_alt = "other"
            
        # if(color == grey or gh_license_alt=="no license" or hf_license=="no license"):
        #     continue
        # Now need to see if the current GH license has been added as a sink yet
        if(gh_license_alt not in (SankeyRelations[hf_license_alt]).keys()):
            (SankeyRelations[hf_license_alt])[gh_license_alt] = {"count":0, "color":color}
                
        ((SankeyRelations[hf_license_alt])[gh_license_alt])["count"] += 1
        
        # track the PTMs and Repos which are analyzed
        analyzedHFPTMS.add(row[hf_repo_url_column])
        analyzedGHRepos.add(row[gh_repo_url_column])
        
# wall of text
print()
print()
print("unanalyzedHFlicenses: ", unanalyzedHFlicenses, '\n')
print()
print("unanalyzedGHlicenses: ", unanalyzedGHlicenses, '\n')
print()
print(f"Percent HF Licenses Analyzed: {100*len(known_HF_licenses) / (len(known_HF_licenses)+len(unanalyzedHFlicenses)):.2f}%")
print(f"Percent GF Licenses Analyzed: {100*len(known_GH_licenses) / (len(known_GH_licenses)+len(unanalyzedGHlicenses)):.2f}%")
print()
print(f"Percent HF Repos Analyzed: {100*len(analyzedHFPTMS)/len(allHFPTMS):.2f}%")
print(f"Percent GF Repos Analyzed: {100*len(analyzedGHRepos)/len(allGHRepos):.2f}%")
print()
print(f"Skipped Relations: {skippedNum}")
print(f"Total Number of Covered Relations: {totalRelationsCNT}")
print(f"Identical Relations: {identicalRelations} -- > ", end='')
print(f"{100*identicalRelations/totalRelationsCNT:.2f}%")
print(f"Compatible Relations: {numCompatible} --> ", end='')
print(f"{100*numCompatible/totalRelationsCNT:.2f}%")
print(f"Incompatible Relations: {numIncompatible} --> ", end='')
print(f"{100*numIncompatible/totalRelationsCNT:.2f}%")
print(f"Unknown Relations: {numUnkown} --> ", end='')
print(f"{100*numUnkown/totalRelationsCNT:.2f}%")


# process SankeyRelations to display the Sankey Diagram
allLicenses = [] 
sourceLicenses = {}
targetLicenses = {}
x_positions = []
sourceIDXs = []
targetIDXs = []
colors = []
counts = []
for hf_l in SankeyRelations.keys():
    if hf_l not in sourceLicenses.keys():
        source_i = len(allLicenses)
        allLicenses.append(hf_l)
        sourceLicenses[hf_l] = source_i
    else:
        source_i = sourceLicenses[hf_l]
    for gh_l in (SankeyRelations[hf_l]).keys():
        if gh_l not in targetLicenses.keys():
            target_i = len(allLicenses)
            allLicenses.append(gh_l)
            targetLicenses[gh_l] = target_i
        else:
            target_i = targetLicenses[gh_l]
        sourceIDXs.append(source_i)
        targetIDXs.append(target_i)
        colors.append((SankeyRelations[hf_l])[gh_l]["color"])
        counts.append((SankeyRelations[hf_l])[gh_l]["count"])
        

# Set up the Sankey diagram
fig = go.Figure(data=[go.Sankey(
    arrangement="freeform",
    node=dict(
        pad=30,
        thickness=20,
        line=dict(color='black', width=0.6),
        label=allLicenses,
    ),
    link=dict(
        source=sourceIDXs,
        target=targetIDXs,
        color=colors,
        value=counts,
    )
)])

# Customize layout
fig.update_layout(title_text="", font_size=35)
fig.update_yaxes(ticklabelposition = "outside")
# Show the figure
fig.show()