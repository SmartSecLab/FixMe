import pandas as pd
import json
from pathlib import Path

from warnings import simplefilter

from source.utility import util
import source.refs as ref

simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


def map_rename(columns):
    """Create a renaming mapping dictionary"""
    rename_mapping = {}
    for key in columns.keys():
        rename_mapping[key] = key.split(".")[-1]
    return rename_mapping


def extract_descriptions(descriptions):
    """Extract the descriptions from the descriptions column"""
    desc = []
    if descriptions:
        desc = [descriptions[i]["value"] for i in range(len(descriptions))]
    return desc


def extract_refs(refs_list):
    """Extract the references from the references column"""
    refs = []
    if refs_list:
        refs = [refer["url"] for refer in refs_list]
    return refs


def extract_cwe(problemTypes):
    """Extract the CWE IDs from the problemTypes column"""
    cwes = [
        entry["cweId"]
        for pt in problemTypes
        for entry in pt.get("descriptions", [])
        if "cweId" in entry
    ]
    return cwes if cwes else ["unknown"]


def extract_capec(capec):
    """Extract the CAPEC IDs from the capec column"""
    capecs = []
    if isinstance(capec, list):
        capecs = [entry["capecId"] for entry in capec if "capecId" in entry]
    elif isinstance(capec, dict) and "capecId" in capec:
        capecs = [capec["capecId"]]
    return capecs


def extract_metrics(metrics):
    """Iterate through the list and extract nested items"""
    df = pd.DataFrame()
    for item in metrics:
        for parent_key, parent_value in item.items():
            if isinstance(parent_value, dict):
                parent_df = pd.DataFrame(parent_value, index=[0])
                parent_df.columns = [
                    f"{parent_key}_{col}" for col in parent_df.columns]
                df = pd.concat([df, parent_df], axis=1)
            else:
                df[parent_key] = parent_value
    return df


def append_cve(df, df_cve):
    """Fill the missing columns in the DataFrames"""
    # Get all columns from both DataFrames
    all_cols = set(df.columns).union(df_cve.columns)

    # Ignore 'x_legacy' columns
    all_cols = [col for col in all_cols if 'x_legacy' not in col]

    # Filter columns
    df_cve = df_cve.reindex(columns=all_cols, fill_value=None)

    return pd.concat([df, df_cve], ignore_index=True, sort=False)


def extract_cna(cvedict):
    """Extract the CNA data from the cvedict"""
    df_cna = pd.json_normalize(cvedict["containers"]["cna"])
    # Apply transformations conditionally
    transformations = [
        ("references", extract_refs),
        ("descriptions", extract_descriptions),
        ("problemTypes", extract_cwe),
        ("impacts", extract_capec),
    ]

    for col, func in transformations:
        if col in df_cna.columns and df_cna[col].any():
            df_cna[col] = df_cna[col].apply(func)
        else:
            df_cna[col] = None

    # Handle metrics separately
    if "metrics" in df_cna.columns and df_cna["metrics"].any():
        df_metrics = extract_metrics(df_cna["metrics"][0])
        df_cna = pd.concat([df_cna, df_metrics], axis=1)

    df_cna.columns = df_cna.columns.map(lambda x: x.replace(".", "_"))
    return df_cna


def json2df(json_file):
    """Convert JSON data to a pandas DataFrame"""
    # Read JSON data from file
    df_cve = pd.DataFrame()
    if Path(json_file).is_file():
        with open(json_file, "r") as f:
            cvedict = json.load(f)
        df_cna = pd.json_normalize(cvedict["containers"]["cna"])
        df_cna = extract_cna(cvedict)
        df_meta = pd.json_normalize(cvedict["cveMetadata"])
        # concatenate these two dataframes
        df_cve = pd.concat([df_meta, df_cna], axis=1)
    else:
        print(f"File not found: {json_file}")
    return pd.DataFrame(df_cve)


def merge_json_files(json_files):
    """Merge all the JSON files into a single DataFrame"""
    print("=" * 20 + "Merging JSON files" + "=" * 20)
    print(f"#JSON files to scan: {len(json_files)}")
    print("=" * 40)
    df = pd.DataFrame()

    for json_file in json_files:
        df_cve = json2df(json_file)
        if len(df_cve) > 0 and "cveId" in list(df_cve.columns):
            if df.empty:
                df = df_cve[[
                    col for col in df_cve.columns if 'x_legacy' not in col]]
            else:
                df = append_cve(df, df_cve)

        if len(df) % 1000 == 0:
            print(f"#files scanned so far: {len(df)} [shape: {df.shape}]")
            print("=" * 40)

    df = df.dropna(axis=1, how="all")
    return df


def filter_cves_to_update(cve_ids):
    # remove the these CVEs from the the database table of cve records
    if cve_ids:
        print(f"Removing {len(cve_ids)} records from the table...")
        util.cur.execute(
            f"DELETE FROM cve WHERE cveId IN ({', '.join(['?']*len(cve_ids))})", cve_ids)
        util.conn.commit()
    else:
        print("No matching records to filter CVEs.\n")


def save_cve(df):
    """Save the CVE records to a SQLite database"""
    # remove duplicate columns
    print("\n" + "=" * 20 + "Saving CVE" + "=" * 20)
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
    if util.table_exists("cve") and util.config["INCREMENTAL_UPDATE"] is True:
        print(f'Shape of the existing table: {util.get_table_shape("cve")}')

        # find recorded CVEs in the database
        cve_ids = util.get_col_values('cve', 'cveId')

        # find intersection of the CVEs in the database and the new CVEs
        same_cves = list(
            set(list(df['cveId'])).intersection(set(cve_ids)))
        print(f"#CVEs to be updated: {same_cves}")

        # remove the existing records before appending
        filter_cves_to_update(same_cves)

        df.astype(str).to_sql("cve", util.conn,
                              if_exists="append", index=False)
    else:
        df.astype(str).to_sql("cve", util.conn,
                              if_exists="replace", index=False)

    print("Saved/appended CVE records to SQLite!")
    print("#CVE records: ", df.shape)

    print(f'Shape of CVE records[full]: {util.get_table_shape("cve")}')
    print("=" * 50)
    return df


def get_cols(table_name):
    # Connect to the SQLite database
    cursor = util.conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    cols = [col[1] for col in columns]
    return cols


def flatten_cve(cve_dir):
    """Flatten the CVE JSON files and save the records to a SQLite database"""
    print("\n" + "=" * 20 + "Flatten CVEs" + "=" * 20)
    # eg. /Users/guru/research/FixMe/data/cvelistV5
    cve_repo_local = cve_dir + \
        Path(util.config["REPO_URL"]).stem

    mod_files = ref.clone_or_pull(util.config["REPO_URL"], cve_repo_local)

    if util.table_exists("cve") and util.config["INCREMENTAL_UPDATE"] is True:
        print("Updating the existing records [incremental]...")

        json_files = ref.get_mod_cves(mod_files, cve_dir)

        print(f"#URL links to process: {len(json_files)}")

    else:
        print("Collecting all records...")
        json_files = ref.find_json_files(cve_dir)

    df = pd.DataFrame()

    if json_files:
        patch_links = ref.find_urls(json_files)

        cve_files = list(patch_links.keys())
        print(f"#Patch links to process: {len(cve_files)}\n")

        if cve_files:
            df = merge_json_files(cve_files)
            df = save_cve(df)
    return df
