# This script is used to find all the URLs from the CVE JSON files
# Scanning CVEs for git-based commit URLs
import os
import glob
import re
import git
from pathlib import Path


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
    print("#URL links:", len(patch_links))
    return patch_links


def clone_or_pull(repo_url, repo_path):
    """Clone the repo if it doesn't exist, or pull if it does."""
    print("=" * 50)
    mod_files = []
    print(f"\nCloning or pulling {repo_url} to {repo_path}")
    if os.path.exists(repo_path):
        # repo exists, perform a git pull
        try:
            repo = git.Repo(repo_path)
            origin = repo.remotes.origin
            # Store the current commit before pulling
            current_commit = repo.head.commit
            origin.pull()
            print("Git pull successful")
            # Compare current commit with the latest one after pull
            for item in repo.head.commit.diff(current_commit):
                mod_files.append(item.a_path)
        except git.exc.GitCommandError as e:
            print("Error occurred during git pull:", e)
    else:
        # repo doesn't exist, perform a git clone
        try:
            git.Repo.clone_from(repo_url, repo_path)
            print("Git clone successful")
        except git.exc.GitCommandError as e:
            print("Error occurred during git clone:", e)
    print("=" * 50)
    return mod_files


def get_mod_cves(mod_files, data_dir):
    """Find the modified CVE JSON files after a git pull"""
    mod_cves = []
    if mod_files:
        # print(f"Modified files after git pull: {mod_files}")
        mod_cves = [Path(data_dir, 'cvelistV5', file)
                    for file in mod_files if file.endswith(".json") and "CVE" in file]
        print(f"Modified/New CVEs: \n{mod_cves}")
        print(f"#modified CVEs: {len(mod_cves)}")

        # TODO: remove these lines
        with open(data_dir + "mod_cves.txt", "w") as f:
            f.write("\n".join([str(cve) for cve in mod_cves]))

    return mod_cves
