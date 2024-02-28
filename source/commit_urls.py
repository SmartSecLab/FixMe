# This script is used to find all the URLs from the CVE JSON files
# Scanning CVEs for git-based commit URLs


import os
import pandas as pd
import glob


def find_json_files(directory):
    """Find all JSON files in the given directory (including subdirectories)."""
    json_files = glob.glob(os.path.join(
        directory, "**/*.json"), recursive=True)
    return json_files


def find_commit_urls(urls):
    """collect all the URLs of they are commit hashes"""
    commit_urls = [url for url in urls if "commit" in url]
    return commit_urls


def find_urls(json_files):
    """collect all the URLs from the CVE Json files"""
    patch_links = {}

    if json_files:
        # print(f"JSON files found: {len(json_files)}")
        for json_file in json_files:
            refs = []
            if os.path.isfile(json_file):
                # try:
                df = pd.read_json(json_file)
                if "containers" in df.columns:
                    contr = df.containers
                    if "cna" in contr:
                        cna = df.containers.cna
                        if "references" in cna.keys():
                            refs = df.containers.cna['references']
                            # print(f'{json_file} has refs type: \n{refs}')
                        #     if "reference_data" in refs:
                        #         refs = refs['reference_data']
                        #         print(f'{json_file} has reference_data')
                        #     # else:
                        #     #     print(f'{json_file} does not have reference_data')
                        # # else:
                        # #     print(f'{json_file} does not have references')
                    else:
                        print(f'{json_file} does not have cna')
                else:
                    print(f'{json_file} does not have containers')

                if refs:
                    urls = [ref["url"] for ref in refs if "url" in ref]
                    commit_urls = find_commit_urls(urls)
                else:
                    urls = []
                    commit_urls = []

                if commit_urls:
                    patch_links[json_file] = commit_urls

                # except Exception as exec:
                #     print(f"Error reading JSON file {json_file}: {exec}")

    else:
        print("No JSON file found in the directory.")
    return patch_links


if __name__ == "__main__":
    json_files = find_json_files("data/cvelistV5-main/cves/2024/24xxx/")
    patch_links = find_urls(json_files)
    print(f"Number of URL links: {len(patch_links)}")
