import os
from pathlib import Path
import sqlite3
import yaml


class UtilityManager:
    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.repo_name = Path(self.config["REPO_URL"]).stem

        Path("figure").mkdir(parents=True, exist_ok=True)
        Path(self.config["DATA_DIR"]).mkdir(parents=True, exist_ok=True)

        self.db_file = self.config['DB_FILE']
        if self.config['FRESH_MINE']:
            print(f"Cleaning the database: {self.db_file}")
            os.remove(self.db_file)
        else:
            print(f"Using the existing database: {self.db_file}")

        self.conn = sqlite3.connect(self.db_file)
        self.cur = self.conn.cursor()
        print("Connected to SQLite!")

    @staticmethod
    def load_config(config_file):
        with open(config_file, "r") as file:
            config = yaml.safe_load(file)
        return config

    def table_exists(self, table_name):
        """Check if a table exists in the SQLite database"""
        sql = f"SELECT name FROM sqlite_master WHERE type='table'" \
            f"AND name='{table_name}'"
        self.cur.execute(sql)
        result = self.cur.fetchone()
        return result if result else False

    def get_col_values(self, table, column):
        """Get all the values from a specific column in a table"""
        self.cur.execute("SELECT " + column + " FROM " + table)
        result = self.cur.fetchall()
        result = [x[0] for x in result]
        return result if result else False

    def get_table_shape(self, table_name):
        """Execute a query to show shape"""
        util.cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        num_rows = util.cur.fetchone()[0]

        util.cur.execute(f"PRAGMA table_info({table_name})")
        columns = util.cur.fetchall()
        column_names = [column[1] for column in columns]
        return (num_rows, len(column_names))

    def save_table(self, df, table_name="patch_collection"):
        """Save the DataFrames to sqlite3 database"""
        print("=" * 50)
        print(f"Saving {table_name}...")
        if not df.empty:
            if util.table_exists(table_name) and util.config["INCREMENTAL_UPDATE"] is True:
                print(f'{table_name} shape: {util.get_table_shape(table_name)}')
                df.astype(str).to_sql(table_name, util.conn,
                                      if_exists="append", index=False)
            else:
                print(f"Creating {table_name} table...")
                df.astype(str).to_sql(table_name, util.conn,
                                      if_exists="replace", index=False)
            print(f"Patches/Hunks: {df.shape}")
        else:
            print(f"No data to save in {table_name}.")
        print("=" * 50)

    def close_connection(self):
        """Close the SQLite connection"""
        self.conn.close()
        print("SQLite connection closed!")

    def get_language_from_ext(self, file_path):
        """Get the programming language from the file extension"""
        extension = file_path.split(".")[-1].lower()
        language_mapping = {
            "c": "C",
            "h": "C",
            "cpp": "C++",
            "hpp": "C++",
            "java": "Java",
            "py": "Python",
            "js": "JavaScript",
            "html": "HTML",  # Markup language, not a programming language
            "htm": "HTML",
            "css": "CSS",  # Style sheet language, not a programming language
            "php": "PHP",
            "rb": "Ruby",
            "swift": "Swift",
            "cs": "C#",
            "vb": "Visual Basic",
            "go": "Go",
            "rust": "Rust",
            "ts": "TypeScript",
            "dart": "Dart",
            "pl": "Perl",
            "lua": "Lua",
            "sh": "Shell script",
            "ps1": "PowerShell script",
            "jsx": "JSX",  # JavaScript extension used with React
            "tsx": "TypeScript with JSX",  # Used with React
            "r": "R",
            "scala": "Scala",
            "jl": "Julia",
            "matlab": "MATLAB",
            "asm": "Assembly",
            "sql": "SQL",  # Query language, not a programming language
            "kt": "Kotlin",
            "vue": "Vuejs",  # JavaScript framework
            "scss": "SASS",  # CSS preprocessor
            "sass": "SASS",
        }
        return language_mapping.get(extension, "Unknown")


util = UtilityManager("config.yaml")
