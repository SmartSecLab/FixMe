# This script is used to find all the URLs from the CVE JSON files
# Scanning CVEs for git-based commit URLs


import urllib.request
from unidiff import PatchSet
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import json
from pandas import json_normalize
from tabulate import tabulate
import glob
# time of execution
import time
from pathlib import Path
from tabulate import tabulate
import itertools
# import sqlite3
import sqlite3
from sqlite3 import Error
import yaml

# customs
import source.utility as utils


def find_json_files(directory):
    """Find all JSON files in the given directory (including subdirectories).
    """
    json_files = glob.glob(os.path.join(
        directory, '**/*.json'), recursive=True)
    return json_files


def find_commit_urls(urls):
    """collect all the URLs of they are commit hashes
    """
    commit_urls = [url for url in urls if 'commit' in url]
    return commit_urls


def find_urls(json_files):
    """collect all the URLs from the CVE Json files
    """
    patch_links = {}

    if json_files:
        # print(f"JSON files found: {len(json_files)}")
        for json_file in json_files:
            if os.path.isfile(json_file):
                try:
                    # with open(json_file, 'r') as f:
                    df = pd.read_json(json_file)
                    refs = df.containers.cna['references']
                    urls = [ref['url'] for ref in refs if 'url' in ref]
                    commit_urls = find_commit_urls(urls)

                    if commit_urls:
                        patch_links[json_file] = commit_urls

                except Exception as exec:
                    print(f'Error reading JSON file {json_file}: {exec}')

    else:
        print("No JSON file found in the directory.")
    return patch_links


if __name__ == '__main__':
    json_files = find_json_files('data/cvelistV5-main/cves/2024/24xxx/')
    patch_links = find_urls(json_files)
    print(f'Number of URL links: {len(patch_links)}')
