# collect complete data


import pandas as pd

import source.hunks as hunk
import source.patchset as ps

# customs
import source.utility as utils

if __name__ == "__main__":
    # check if repository table exists
    if not utils.table_exists("repository"):
        print(
            "Repository table does not exist. ",
            "Please run collect_repos.py to collect repo URLs.",
        )
        urls = ps.collect_repos().url
    else:
        # load repository table from sqlite3 database
        print("Loading URLs from database...")
        urls = list(pd.read_sql_query(
            "SELECT url FROM repository", utils.conn).url)
    print(f"Found {len(urls)} URLs.")

    # collect hunks
    hunk.collect_repo_hunks(urls)
