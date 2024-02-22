import source.utility as utils
import pandas as pd
import json
from pandas import json_normalize


import source.utility as utils
import source.commit_urls as cve


def map_rename(columns):
    """Create a renaming mapping dictionary"""
    rename_mapping = {}
    for key in columns:
        rename_mapping[key] = key.split(".")[-1]
    return rename_mapping


# json_file = 'cvelistV5-main/cves/2024/21xxx/CVE-2024-21309.json'


def json2df(json_file):
    """Convert JSON data to a pandas DataFrame"""
    # Read JSON data from file
    with open(json_file, "r") as f:
        json_data = json.load(f)

    df = json_normalize(json_data, max_level=5)
    df = df.rename(columns=map_rename(df.columns))
    return df


# function to merge all json files into a single dataframe


def merge_json_files(json_files):
    """Merge all the JSON files into a single DataFrame"""
    # totoal number of json files
    print("=" * 20 + "Merging JSON files" + "=" * 20)
    print(f"#JSON files to scan: {len(json_files)}")
    print("=" * 40)
    df = pd.DataFrame()
    for json_file in json_files:
        try:
            df_json = json2df(json_file)
            # dfs = [json2df(json_file) for json_file in json_files]
            # print(f'Number of DataFrames: {len(dfs)}')
            # try:
            if "cveId" in list(df_json.columns):
                if df.empty:
                    df = df_json
                else:
                    unique_cols = list(
                        set(list(df.columns) + list(df_json.columns)))
                    # insert new columns with None values
                    for column in unique_cols:
                        if column not in list(df.columns):
                            df[column] = None
                        if column not in list(df_json.columns):
                            df_json[column] = None

                    df = df.sort_index(axis=1)
                    df_json = df_json.sort_index(axis=1)

                    df = pd.concat(
                        [df, df_json], ignore_index=True, sort=False)
                # print('='*20)
            # verbose how many files have been processed
            if len(df) % 500 == 0:
                print(f"#files scanned: {len(df)}")
                print("=" * 40)

        except Exception as exec:
            print(f"Error: {exec}")
            print(f"Error reading file: {json_file}")
            continue
    print(f"Number of DataFrames: {len(df)}")
    return df


def extract_cwe(problemTypes):
    """Extract the CWE IDs from the problemTypes column"""
    cwes = []
    if problemTypes:
        items = [problemTypes[i]["descriptions"]
                 for i in range(len(problemTypes))]
        for item in items:
            for entry in item:
                if "cweId" in entry:
                    cwes.append(entry["cweId"])
    if not cwes:
        cwes = ["unknown"]
    return cwes


def flatten_cve(cve_dir):
    """Flatten the CVE JSON files and save the records to a SQLite database"""
    json_files = cve.find_json_files(cve_dir)
    patch_links = cve.find_urls(json_files)
    print(f"Number of URL links: {len(patch_links)}")

    json_files = list(patch_links.keys())
    df = merge_json_files(json_files)
    df["cwe"] = df["problemTypes"].apply(extract_cwe)

    # remove duplicate columns
    cols = list(df.columns)
    duplicate_cols = [col for col in cols if cols.count(col) > 1]
    dedup_cols = list(set(duplicate_cols))
    print(f"Duplicate columns: {dedup_cols}")
    df = df.drop(columns=dedup_cols, axis=1)

    if "STATE" in df.columns:
        df = df.rename(columns={"STATE": "meta_state"})
    if "title" in df.columns:
        df = df.rename(columns={"title": "meta_title"})

    # Save the dataframe to a sqlite database
    # Convert the type of the columns to string
    # otherwise, the sqlite3 will raise an error
    df.astype(str).to_sql("cve", utils.conn, if_exists="replace", index=False)
    # df.to_csv(output_dir + 'cve.csv', index=False)
    print("Saved flatten_CVE records to SQLite database")
    print("#records: ", df.shape)
    print("=" * 40)
    return df


if __name__ == "__main__":
    df = flatten_cve(utils.CVE_DIR)
    print(df.head())
