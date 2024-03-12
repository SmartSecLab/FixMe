import pandas as pd
import git
import source.hunks as hunk
import source.repository as ps
from pathlib import Path

# customs
from source.utility import util
import source.refs as ref
import source.cve as cve


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

    # collect hunks
    hunk.collect_repo_hunks(urls)


def get_urls_from_db(conn):
    """Get the references from the database"""
    # check if cve table exists
    urls = []
    if not util.table_exists("cve"):
        print("CVE table does not exist.")
    else:
        urls = pd.read_sql_query("SELECT `references` FROM cve;", conn)
        urls = list(urls.apply(eval).explode())
    print(f"#References from the database: {len(urls)}")
    return urls


if __name__ == "__main__":

    # STEP 1: collect modified/new files
    # # eg. /Users/guru/research/FixMe/data/cvelistV5
    # cve_repo_local = util.config["DATA_DIR"] + \
    #     Path(util.config["REPO_URL"]).stem

    # mod_files = ref.clone_or_pull(util.config["REPO_URL"], cve_repo_local)
    # mod_jsons = ref.get_mod_cves(mod_files, util.config["DATA_DIR"])

    # STEP 2: collect commit URLs
    # if mod_urls:

    # STEP 3: get URLs from the database
    # urls_from_db = get_urls_from_db(util.conn)

    # STEP 4: compare the URLs
    # new_urls = [url for url in mod_urls if url not in urls_from_db]
    # print(f"#URLs to be extracted: {len(mod_urls)}")
    # print(f"URLs to be extracted: {mod_urls}")

    # STEP 3: flatten the CVE JSON files
    df_cve = cve.flatten_cve(util.config["DATA_DIR"])

    # STEP 4: load the URLs from the database or collect them
