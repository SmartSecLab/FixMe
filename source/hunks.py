# Parsing git patch to collect hunks

import source.utility as utils
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
import pandas as pd
from urllib.parse import urlparse

# customs
import source.utility as utils
import source.patchset as ps


def parse_before_after_code(hunk):
    """Parse the before and after code from a hunk
    """
    before_code = []
    after_code = []
    for line in hunk:
        if line.is_removed or line.is_context:
            # This line is part of the before code
            before_code.append(str(line)[1:])  # Exclude the '-' at the start
        if line.is_added or line.is_context:
            after_code.append(str(line)[1:])  # Exclude the '+' at the start

    # Join the lines of code into strings
    before_code = ''.join(before_code)
    after_code = ''.join(after_code)
    return before_code, after_code


def on_each_patch_file(patched_file):
    # Loop over each hunk in the patched file
    hunks = []
    for hunk in patched_file:
        # Parse the before and after code
        before_code, after_code = parse_before_after_code(hunk)
        hunk_data = {
            'file': patched_file.path,
            'hunk': str(hunk),
            'hunk_patch': str(hunk),
            'source': hunk.source,
            'target': hunk.target,
            'source_lines': hunk.source_lines,
            'target_lines': hunk.target_lines,
            'added_lines': [str(line)[1:] for line in hunk if line.is_added],
            'removed_lines': [str(line)[1:] for line in hunk if line.is_removed],
            'before_code': before_code,
            'after_code': after_code,
            'source_start': hunk.source_start,
            'source_length': hunk.source_length,
            'target_start': hunk.target_start,
            'target_length': hunk.target_length,
            'section_header': hunk.section_header,
            'hunk_length': len(hunk),
        }
        # Append the hunk data to the patch_hunks list
        hunks.append(hunk_data)
    return hunks


def parse_patchset(patch):
    """Parse the hunks from a patch
    """
    # Loop over each patched file in the diff
    patch_meta = {}
    patch_hunks = []

    for patched_file in patch:
        # all_attrs = dir(patched_file)
        file_attrs = {}

        for attr in patched_file.__dict__:
            # Exclude attrs that start with '__' (dunder/magic methods)
            if not attr.startswith('__'):
                attr_value = getattr(patched_file, attr)
                file_attrs[attr] = attr_value

        patch_meta[patched_file.path] = file_attrs
        # Loop over each hunk in the patched file
        file_hunks = on_each_patch_file(patched_file)
        patch_hunks.extend(file_hunks)
    return patch_meta, patch_hunks


def collect_repo_hunks(urls):
    """Collect hunks from the repository
    """
    df_repo_patch = pd.DataFrame()
    df_repo_hunks = pd.DataFrame()

    for url in urls:
        try:
            patch = ps.get_patch_from_url(url)
            patch_meta, patch_hunks = parse_patchset(patch)

            df_hunk = pd.DataFrame(patch_hunks)

            df_file = pd.DataFrame.from_dict(
                patch_meta, orient='index').reset_index()
            df_file = df_file.rename(columns={'index': 'file'})
            df_file['url'] = url

            # Append the DataFrames to the collection
            df_repo_patch = pd.concat(
                [df_repo_patch, df_file], ignore_index=True)
            df_repo_hunks = pd.concat(
                [df_repo_hunks, df_hunk], ignore_index=True)
        except Exception as exec:
            print(f'Error: {exec}')
            continue

    # Save the DataFrames to sqlite3 database
    df_repo_patch.astype(str).to_sql('patch_collection', utils.conn,
                                     if_exists='replace', index=False)
    df_repo_hunks.astype(str).to_sql('hunk_collection', utils.conn,
                                     if_exists='replace', index=False)
    return df_repo_patch, df_repo_hunks


if __name__ == "__main__":
    print('Parsing git patch to collect hunks...')
    # load repository table from sqlite3 database
    urls = list(pd.read_sql_query(
        'SELECT url FROM repository', utils.conn).url)
    print('='*50)
    print(f'Parsing patches from {len(urls)} repositories...')
    print('This may take a while...')
    collect_repo_hunks(urls)

# def parse_patch(patch):
#     """parse patch and convert it into dataframe
#     """
#     # Access information about each file in the patchset
#     data = {'file': [], 'removed': [], 'added': [], 'unchanged': [], 'pl': []}

#     for patched_file in patch:
#         for hunk in patched_file:
#             added_lines = [line.value.strip()
#                            for line in hunk if line.is_added]
#             removed_lines = [line.value.strip()
#                              for line in hunk if line.is_removed]
#             unchanged_lines = [line.value.strip(
#             ) for line in hunk if not line.is_added and not line.is_removed]

#             data['file'].append(patched_file.path)
#             data['added'].append('\n'.join(added_lines))
#             data['removed'].append('\n'.join(removed_lines))
#             data['unchanged'].append('\n'.join(unchanged_lines))
#             data['pl'].append(utils.get_language_from_ext(patched_file.path))
#     return data

# url = 'https://github.com/torvalds/linux/commit/3f24fcdacd40c70dd2949c1cfd8cc2e75942a9e3'
# patch = get_patch_from_url(url)
# col_dfs = ps.collect_repos(utils.flatten_cve(utils.CVE_DIR))


# def scan_all(col_dfs):
#     urls = list(col_dfs['references'].url)

#     github_urls = [url for url in urls if 'commit' in url]
#     df_patch = collect_patches(github_urls)

#     df_patch.to_csv(f'{utils.output_dir}/patches.csv', index=False)

#     # Save the DataFrame to sqlite3 database
#     df_patch.astype(str).to_sql(
#         'patch', utils.conn, if_exists='replace', index=False)


# def collect_patches(github_urls):
#     """collect patches of the given URLs
#     """
#     df = pd.DataFrame()
#     for url in github_urls:
#         try:
#             patch = ps.get_patch_from_url(url)
#             data = parse_patch(patch)
#             df_patch = pd.DataFrame(data)
#             df_patch['url'] = url
#             df = pd.concat([df, df_patch]) if len(data) > 0 else df
#         except Exception as exec:
#             print(f'Error processing {url}: \n{exec}')
#     return df.reset_index(drop=True)
