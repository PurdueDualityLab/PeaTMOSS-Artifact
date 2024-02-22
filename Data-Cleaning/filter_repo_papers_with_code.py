import os
import time
import httpcore  # Import httpcore to catch its exceptions
from paperswithcode import PapersWithCodeClient
import json
from tqdm import tqdm

client = PapersWithCodeClient()
json_path = "./github_reuse_repo_data.json"
all_collected_repos = []
num_items_per_page = 500

def fetch_repositories(page, items_per_page):
    try:
        return client.repository_list(page=page, items_per_page=items_per_page), None
    except httpcore.ReadTimeout as e:
        return None, e

all_repositories, error = fetch_repositories(page=1, items_per_page=num_items_per_page)
if all_repositories is not None:
    num_pages = int(all_repositories.count) // num_items_per_page

    for each_page in tqdm(range(num_pages)):
        success = False
        retries = 0
        max_retries = 5
        backoff_factor = 1.5

        while not success and retries < max_retries:
            all_repositories_, error = fetch_repositories(page=each_page + 1, items_per_page=num_items_per_page)
            if error:
                wait_time = backoff_factor ** retries
                print(f"ReadTimeout error encountered. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                retries += 1
            else:
                success = True
                for each_repo in all_repositories_.results:
                    all_collected_repos.append(each_repo.url)

        if not success:
            print(f"Failed to fetch repositories for page {each_page + 1} after {max_retries} retries.")

    print("Total repos found in PapersWithCode database:", len(all_collected_repos))
else:
    print("Failed to fetch initial repository list. Please check your network connection or the PapersWithCode API status.")



# Compare with Peatmoss URLs to remove the research paper implementations and model zoos
file_p = open(json_path, 'r')
json_data = json.loads(file_p.read())
print("All collected repos (first five):", all_collected_repos[:5])
filtered_repos = []
filtered_repos_found = []
print("Removing repos that are published in PapersWithCode...")
for each_repo in tqdm(json_data):
    if "https://"+str(each_repo['reuse_repository_url']) not in all_collected_repos:
        filtered_repos.append(each_repo)
    else:
        filtered_repos_found.append(each_repo)


json_obj_not_found = json.dumps(filtered_repos, indent=4)
json_obj_found = json.dumps(filtered_repos_found, indent=4)
with open("./github_reuse_filtered_not_found.json", "w") as f:
    f.write(json_obj_not_found)
with open("./github_reuse_filtered_found.json", "w") as f:
    f.write(json_obj_found)
print("Repos in PeatMoss before filtering :", len(json_data))
print("Repos in PeatMoss after filtering :", len(filtered_repos))
file_p.close()

# write a text file for Repoquester tool
filtered_repos_loaded = json.load(open("./github_reuse_filtered_not_found.json", "r"))
filtered_urls = []
print("Number of repos in PeatMoss after filtering :", len(filtered_repos_loaded))
for each_repo in filtered_repos_loaded:
    url_ = each_repo['reuse_repository_url'].split("//")[-1].split("/")
    filtered_urls.append(url_[1] + "/" + url_[2])

#remove duplicates
filtered_urls = list(set(filtered_urls))
with open("./repoquester_input.txt", "w") as f:
    for each_repo in filtered_urls:
        f.write(each_repo + "\n")
print("Repoquester input file written with", len(filtered_urls), "repos.")
print("After removing the duplicate repos, the number of repos is", len(set(filtered_urls)))
