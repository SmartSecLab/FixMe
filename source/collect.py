import pandas as pd
import git
from pathlib import Path

# customs
import source.cve as cve
import source.hunks as hunk
import source.refs as ref
import source.repository as repo
from source.utility import util


def get_urls_from_db(df):
    """Get the references and CVE IDs from the database"""
    # Check if cve table exists
    print("="*50)
    if util.table_exists("cve"):
        if util.table_exists("repository") and util.config["INCREMENTAL_UPDATE"] is True:
            print("Updating repositry records [incremental]...")
            if not df.empty:
                df['references'] = df.references.explode().reset_index(drop=True)
            else:
                print("No references found in new data.")
        else:
            print("Loading references from database...")
            df = pd.read_sql_query(
                "SELECT `cveId`, `references` FROM cve;", util.conn)

            if not df.empty:
                df['references'] = df.references.apply(
                    eval).explode().reset_index(drop=True)
            else:
                print("No references found in the database.")
    print(f"#References from database(shape): {df.shape}")
    print("="*50)
    return df[["cveId", "references"]] if not df.empty else df


if __name__ == "__main__":
    # STEP 1: collect the modifiesd/new CVE files
    df_cve = cve.flatten_cve(util.config["DATA_DIR"])

    # STEP 2: collect the repository URLs to repository table
    df_ref = get_urls_from_db(df_cve)

    if not df_ref.empty:
        df_repo = repo.parse_commit_urls(df_ref)

        # STEP 3: collect hunks from the repository
        if not df_repo.empty:
            util.save_table(df_repo, "repository")
            hunk.collect_repo_hunks(df_repo.references)
        else:
            print("No repository data found.")

        print("="*50)
        print('Database is up-to-date!')
        print("="*50)
