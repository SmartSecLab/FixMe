# Parsing git patch from commit $hash.diff$

import source.utility as utils
import urllib.request
from unidiff import PatchSet
import pandas as pd
from pandas import json_normalize


import pandas as pd
from urllib.parse import urlparse

# customs
import source.utility as utils
import source.flatten_cve as cve


def get_patch_from_url(url):
    """retrieve patch from the given git-based commit URL."""
    url_diff = url + ".diff"
    # diff = urllib.request.urlopen('https://github.com/ASSERT-KTH/RewardRepair/commit/2509b5e91e2e80b6b84da3d8cd0e1d1748c0ecfc.diff')
    diff = urllib.request.urlopen(url_diff)
    encoding = diff.headers.get_charsets()[0]
    patch = PatchSet(diff, encoding=encoding)
    return patch


def parse_vcs_url(url):
    """Parse the version control URL"""
    try:
        parsed_url = urlparse(url)
        # Combine the scheme and netloc to form the base URL
        base_url = parsed_url.scheme + "://" + parsed_url.netloc
        # Split the path by '/'
        path_components = parsed_url.path.split("/")
        # Extract the version control system and repository
        if "github.com" in parsed_url.netloc:
            vcs = "GitHub"
            repository = base_url + "/" + \
                path_components[1] + "/" + path_components[2]
            commit_hash = (
                path_components[4]
                if len(path_components) > 4 and path_components[3] == "commit"
                else None
            )
        elif "gitlab.com" in parsed_url.netloc:
            vcs = "GitLab"
            repository = base_url + "/" + \
                path_components[1] + "/" + path_components[2]
            commit_hash = path_components[5] if len(
                path_components) > 5 else None
        elif "bitbucket.org" in parsed_url.netloc:
            vcs = "Bitbucket"
            repository = base_url + "/" + \
                path_components[1] + "/" + path_components[2]
            commit_hash = (
                path_components[4]
                if len(path_components) > 4 and path_components[3] == "commits"
                else None
            )
        else:
            vcs = None
            repository = None
            commit_hash = None
    except Exception as e:
        vcs = None
        repository = None
        commit_hash = None
    return vcs, repository, commit_hash


def parse_vcs_urls(urls):
    """Parse the version control URLs"""
    vcss = []
    repositories = []
    commit_hashes = []
    # Iterate through URLs and parse them
    for url in urls:
        vcs, repository, commit_hash = parse_vcs_url(url)
        vcss.append(vcs)
        repositories.append(repository)
        commit_hashes.append(commit_hash)
    # Create a DataFrame
    data = {
        "url": urls,
        "vcs": vcss,
        "repository": repositories,
        "commit_hash": commit_hashes,
    }
    return pd.DataFrame(data)


def normalize_list_column(df, column):
    """Normalize a column containing lists
    put all the data into a single dataframe of all column value list
    """
    df_col = pd.DataFrame()
    for index, row in df.iterrows():
        if row[column]:
            df_part = json_normalize(row[column])
            df_part["cveId"] = row["cveId"]
            df_col = pd.concat([df_col, df_part], ignore_index=True)
    return df_col


def save_list_cols(df):
    """Normalize the columns with lists
    put all dataframes into a single dictionary
    """
    col_dfs = {}
    # Check which columns contain lists
    columns_with_lists = [
        col for col in df.columns if df[col].apply(lambda x: isinstance(x, list)).any()
    ]
    # print(f'Columns with list type: \n{columns_with_lists}\n')

    # TODO: Normalize only references column
    for col in columns_with_lists:
        try:
            col_dfs[col] = normalize_list_column(df, column=col)
            # print(tabulate(df_part, headers='keys', tablefmt='psql'))
            # print(f'Table: {col} - {col_dfs[col].shape}')
            # Save dataframes to csv files
            # col_dfs[col].to_csv(utils.output_dir + f"{col}.csv", index=False)
        except Exception as exec:
            print(f"Error: {exec}")
            continue
    return col_dfs


def collect_repos():
    """Collect repositories from the DataFrame"""
    df = cve.flatten_cve(utils.CVE_DIR)
    col_dfs = save_list_cols(df)

    urls = list(col_dfs["references"].url)
    df_repo = parse_vcs_urls(urls)
    df_repo = df_repo.dropna(subset=["commit_hash"])

    # Save the DataFrame to sqlite3 database
    df_repo.astype(str).to_sql(
        "repository", utils.conn, if_exists="replace", index=False
    )
    print("Repositories saved to sqlite3 database")
    print(f"Repositories: {df_repo.shape}")
    return df_repo


if __name__ == "__main__":
    patch = get_patch_from_url(
        "https://github.com/ASSERT-KTH/RewardRepair/commit/2509b5e91e2e80b6b84da3d8cd0e1d1748c0ecfc"
    )
    # patch = get_patch_from_url('https://github.com/PackageKit/PackageKit/commit/64278c9127e3333342b56ead99556161f7e86f79')
    print(f"Patch:/n{patch[0]}")
