# Parsing git patch from commit $hash.diff$
#
import urllib.request
from unidiff import PatchSet
import pandas as pd
from urllib.parse import urlparse

# customs
import source.utility as utils
import source.cve as cve


def get_patch_from_url(url):
    """retrieve patch from the given git-based commit URL."""
    url_diff = url + ".diff"
    diff = urllib.request.urlopen(url_diff)
    encoding = diff.headers.get_charsets()[0]
    patch = PatchSet(diff, encoding=encoding)
    return patch


def split_url(url):
    """Parse the version control URL"""
    vcs = None
    repo = None
    hash = None

    if url:
        try:
            parsed_url = urlparse(url)
            # Combine the scheme and netloc to form the base URL
            base_url = parsed_url.scheme + "://" + parsed_url.netloc
            parts = parsed_url.path.split("/")
            # Extract the version control system and repo
            if "github.com" in parsed_url.netloc:
                vcs = "GitHub"
                repo = base_url + "/" + parts[1] + "/" + parts[2]
                hash = parts[4] if len(
                    parts) > 4 and parts[3] == "commit" else None
            elif "gitlab.com" in parsed_url.netloc:
                vcs = "GitLab"
                repo = base_url + "/" + parts[1] + "/" + parts[2]
                hash = parts[5] if len(parts) > 5 else None
            elif "bitbucket.org" in parsed_url.netloc:
                vcs = "Bitbucket"
                repo = base_url + "/" + parts[1] + "/" + parts[2]
                hash = parts[4] if len(
                    parts) > 4 and parts[3] == "commits" else None
            else:
                vcs = None
                repo = None
                hash = None
        except Exception as e:
            print(f"Error: {e} for URL: {url}")
    return (vcs, repo, hash)


def parse_commit_urls(cveIds, urls):
    """Parse the version control URLs"""
    df = pd.DataFrame()
    if len(urls) > 0:
        df = pd.DataFrame({"cveId": cveIds, "references": urls})

        if isinstance(df.references[0], list):
            # Explode the list of references
            df = df.explode("references").reset_index(drop=True)
            print(f"Length of the references after exploding: {len(df)}")
            df["vcs"], df["repo"], df["hash"] = zip(
                *df.references.apply(split_url))
    else:
        print("No references found in the CVE data.")

    if df.empty:
        print("No data found.")
    else:
        df = df.dropna(subset=["hash"])
        # Remove duplicates based on the cveId and hash (same output)
        df = df.drop_duplicates(
            subset=["cveId", "hash"]).reset_index(drop=True)
        print(f"commit data shape: {df.shape}")
    return df


def collect_repos():
    """Collect repositories from the DataFrame"""
    df_cves = cve.flatten_cve(utils.CVE_DIR)
    df = parse_commit_urls(df_cves.cveId, df_cves.references)

    # Save to sqlite3 database
    df.astype(str).to_sql("repository", utils.conn,
                          if_exists="replace", index=False)
    print("Commit information is saved to sqlite3 database.")
    print(f"Commits: {df.shape}")
    return df


if __name__ == "__main__":
    patch = get_patch_from_url(
        "https://github.com/ASSERT-KTH/RewardRepair/commit/2509b5e91e2e80b6b84da3d8cd0e1d1748c0ecfc"
    )
    print(f"Patch:/n{patch[0]}")
