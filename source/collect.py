# collect complete data
import pandas as pd
import git
import source.hunks as hunk
import source.patchset as ps
from pathlib import Path

# customs
import source.utility as utils
import source.commit_urls as cu
import source.utility as util

if __name__ == "__main__":
    # collect commit URLs
    # Call the clone_or_pull function with the repo URL and path
    cve_repo_path = util.output_dir + Path(util.repo_url).stem
    modified_files = cu.clone_or_pull(util.repo_url, cve_repo_path)

    modified_cve_files = cu.get_modified_cve_files(modified_files, util.output_dir)
    print(modified_cve_files)

    # check if repository table exists
    if not utils.table_exists("repository"):
        print(
            "Repository table does not exist. ",
            "Please run collect_repos.py to collect repo URLs.",
        )
        urls = ps.collect_repos().references
    else:
        # load repository table from sqlite3 database
        print("Loading URLs from database...")
        urls = list(
            pd.read_sql_query("SELECT * FROM repository",
                              utils.conn).references
        )
    print(f"Found {len(urls)} URLs.")

    # collect hunks
    hunk.collect_repo_hunks(urls)
