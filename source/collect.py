import pandas as pd
import git
from pathlib import Path

# customs
import source.cve as cve
import source.hunks as hunk
import source.refs as ref
import source.repository as repo
from source.utility import util


def load_urls():
    """Load the URLs from the database or collect them"""
    # check if repository table exists
    urls = []
    if not util.table_exists("repository"):
        print("Repository table does not exist.")
        # urls = repo.collect_repos().references
    else:
        # load repository table from sqlite3 database
        print("Loading URLs from database...")
        urls = list(
            pd.read_sql_query("SELECT * FROM repository",
                              util.conn).references
        )
    print(f"#URLs from the database: {len(urls)}")
    return urls


def get_urls_from_db(df):
    """Get the references and CVE IDs from the database"""
    # Check if cve table exists
    if not util.table_exists("cve"):
        print("No CVE record in the database!")
        return pd.DataFrame()
    else:
        if util.table_exists("repository") and util.config["INCREMENTAL_UPDATE"] is True:
            print("Updating repositry records [incremental]...")
        else:
            print("Loading references from database...")
            df = pd.read_sql_query(
                "SELECT `cveId`, `references` FROM cve;", util.conn)
            if not df.empty:
                df = df.references.apply(eval).explode()
                print(f"#References from the database: {len(df)}")
            else:
                print("No references found in the database.")
    return df


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
