import os
from pathlib import Path
import sqlite3
import yaml


class DatabaseManager:
    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.repo_name = Path(self.config["REPO_URL"]).stem
        Path("figure").mkdir(parents=True, exist_ok=True)
        Path(self.config["DATA_DIR"]).mkdir(parents=True, exist_ok=True)
        self.db_file = self.config['DB_FILE']

        if self.config['FRESH_MINE']:
            print("Cleaning the database directory!")
            os.remove(self.db_file)

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
        sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        self.cur.execute(sql)
        result = self.cur.fetchone()
        return result if result else False

    def get_col_values(self, table, column):
        """Get all the values from a specific column in a table"""
        self.cur.execute("SELECT " + column + " FROM " + table)
        result = self.cur.fetchall()
        return result if result else False

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


# Example usage:
util = DatabaseManager("config.yaml")
print(util.table_exists("cve"))
