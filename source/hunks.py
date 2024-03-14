# Parsing git patch to collect hunks

import source.utility as utils
import pandas as pd

from source.utility import util
import source.repository as repo


def parse_before_after_code(hunk):
    """Parse the before and after code from a hunk"""
    before_code = []
    after_code = []
    for line in hunk:
        if line.is_removed or line.is_context:
            # This line is part of the before code
            before_code.append(str(line)[1:])  # Exclude the '-' at the start
        if line.is_added or line.is_context:
            after_code.append(str(line)[1:])  # Exclude the '+' at the start

    # Join the lines of code into strings
    before_code = "".join(before_code)
    after_code = "".join(after_code)
    return before_code, after_code


def on_each_patch_file(patched_file):
    # Loop over each hunk in the patched file
    hunks = []
    for hunk in patched_file:
        # Parse the before and after code
        before_code, after_code = parse_before_after_code(hunk)
        hunk_data = {
            "file": patched_file.path,
            "hunk": str(hunk),
            "hunk_patch": str(hunk),
            "source": hunk.source,
            "target": hunk.target,
            "source_lines": hunk.source_lines,
            "target_lines": hunk.target_lines,
            "added_lines": [str(line)[1:] for line in hunk if line.is_added],
            "removed_lines": [str(line)[1:] for line in hunk if line.is_removed],
            "before_code": before_code,
            "after_code": after_code,
            "source_start": hunk.source_start,
            "source_length": hunk.source_length,
            "target_start": hunk.target_start,
            "target_length": hunk.target_length,
            "section_header": hunk.section_header,
            "hunk_length": len(hunk),
        }
        # Append the hunk data to the patch_hunks list
        hunks.append(hunk_data)
    return hunks


def parse_patchset(patch):
    """Parse the hunks from a patch"""
    # Loop over each patched file in the diff
    patch_meta = {}
    patch_hunks = []

    for patched_file in patch:
        # all_attrs = dir(patched_file)
        file_attrs = {}

        for attr in patched_file.__dict__:
            # Exclude attrs that start with '__' (dunder/magic methods)
            if not attr.startswith("__"):
                attr_value = getattr(patched_file, attr)
                file_attrs[attr] = attr_value

        patch_meta[patched_file.path] = file_attrs
        # Loop over each hunk in the patched file
        file_hunks = on_each_patch_file(patched_file)
        patch_hunks.extend(file_hunks)
    return patch_meta, patch_hunks


def collect_repo_hunks(urls):
    """Collect hunks from the repository"""
    print("=" * 50)
    print(f"Parsing patches from {len(urls)} repositories...")
    print("This may take a while...")
    df_repo_patch = pd.DataFrame()
    df_repo_hunks = pd.DataFrame()

    for url in urls:
        try:
            patch = repo.get_patch_from_url(url)
            patch_meta, patch_hunks = parse_patchset(patch)

            df_hunk = pd.DataFrame(patch_hunks)

            df_file = pd.DataFrame.from_dict(
                patch_meta, orient="index").reset_index()
            df_file = df_file.rename(columns={"index": "file"})
            df_file["url"] = url

            # Append the DataFrames to the collection
            df_repo_patch = pd.concat(
                [df_repo_patch, df_file], ignore_index=True)
            df_repo_hunks = pd.concat(
                [df_repo_hunks, df_hunk], ignore_index=True)
        except Exception as exe:
            print(f"Error: {exe} for URL: {url}")
            continue

    util.save_table(df_repo_hunks, "hunk_collection")
    util.save_table(df_repo_patch, "patch_collection")


if __name__ == "__main__":
    # load repository table from sqlite3 database
    urls = list(pd.read_sql_query(
        "SELECT url FROM repository", utils.conn).url)
    collect_repo_hunks(urls)
