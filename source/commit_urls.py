# This script is used to find all the URLs from the CVE JSON files
# Scanning CVEs for git-based commit URLs


import os
import glob
import re


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
    """collect all the URLs from the CVE Json files
    this covers all versions of the CVE records"""
    patch_links = {}
    if json_files:
        for json_file in json_files:
            urls = []
            if os.path.isfile(json_file):
                with open(json_file, "r") as f:
                    urls = re.findall(r'"url": "(.*?)"', f.read())
            if urls:
                patch_links[json_file] = find_commit_urls(urls)
    else:
        print("No JSON file found in the directory.")

    patch_links = {k: v for k, v in patch_links.items() if v}
    return patch_links


if __name__ == "__main__":
    cve_dir = "/Users/guru/research/FixMe/data/cvelistV5/cves/2024/24xxx/"
    json_files = find_json_files(cve_dir)
    print(f"#JSON files: {len(json_files)}")
    patch_links = find_urls(json_files)
    print(f"#URLs: {len(patch_links)}")
    patch_links = find_urls(json_files)
    print(f"Number of URL links: {len(patch_links)}")
