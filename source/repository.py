# Parsing git patch from commit $hash.diff$
#
import re
import requests
import urllib.request
from unidiff import PatchSet
import pandas as pd
from urllib.parse import urlparse
from tabulate import tabulate

# customs
from source.utility import util
import source.cve as cve


def get_commit_message(patch_url):
    """Extract the subject line from a GitHub patch URL."""
    try:
        response = requests.get(patch_url + ".patch")
        response.raise_for_status()
        patch_content = response.text
        subject_match = re.search(
            r'^Subject: (.+)$', patch_content, re.MULTILINE)
        return subject_match.group(1)

    except requests.exceptions.RequestException:
        return "unknown"


def get_patch_from_url(url):
    """retrieve patch from the given git-based commit URL."""
    url_diff = url + ".diff"
    diff = urllib.request.urlopen(url_diff)
    encoding = diff.headers.get_charsets()[0]
    patch = PatchSet(diff, encoding=encoding)
    return patch


def split_url(url):
    """Parse the version control URL"""
    vcs = None
    repo = None
    hash = None

    if url:
        try:
            parsed_url = urlparse(url)
            # Combine the scheme and netloc to form the base URL
            base_url = parsed_url.scheme + "://" + parsed_url.netloc
            parts = parsed_url.path.split("/")
            # Extract the version control system and repo
            if "github.com" in parsed_url.netloc:
                vcs = "GitHub"
                repo = base_url + "/" + parts[1] + "/" + parts[2]
                hash = parts[4] if len(
                    parts) > 4 and parts[3] == "commit" else None
            elif "gitlab.com" in parsed_url.netloc:
                vcs = "GitLab"
                repo = base_url + "/" + parts[1] + "/" + parts[2]
                hash = parts[5] if len(parts) > 5 else None
            elif "bitbucket.org" in parsed_url.netloc:
                vcs = "Bitbucket"
                repo = base_url + "/" + parts[1] + "/" + parts[2]
                hash = parts[4] if len(
                    parts) > 4 and parts[3] == "commits" else None
            else:
                vcs = None
                repo = None
                hash = None
        except Exception as e:
            print(f"Error: {e} for URL: {url}")
    return (vcs, repo, hash)


def parse_commit_urls(df):
    """Parse the version control URLs"""
    if len(df) > 0:
        # if isinstance(df.references[0], list):
        print(f"Shape of repository after exploding: {df.shape}")
        df["vcs"], df["repo"], df["hash"] = zip(
            *df.references.apply(split_url))

    # on the exploded dataframe
    if len(df) > 0:
        print(f'Columns: {df.columns}')
        df = df.dropna(subset=["hash"])
        # Remove duplicates based on the cveId and hash (same output)
        df = df.drop_duplicates(
            subset=["cveId", "hash"]).reset_index(drop=True)
        print(f"commit data shape: {df.shape}")
    else:
        print("No references found in the CVE data.")

    return df


if __name__ == "__main__":
    patch = get_patch_from_url(
        "https://github.com/ASSERT-KTH/RewardRepair/commit/2509b5e91e2e80b6b84da3d8cd0e1d1748c0ecfc"
    )
    print(f"Patch:/n{patch[0]}")
