import os


from pathlib import Path


import sqlite3
import yaml


def load_config(config_file):
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    return config


def table_exists(table_name):
    """Check if a table exists in the SQLite database"""
    cur.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    )
    return cur.fetchone() is not None


config = load_config("config.yaml")

CVE_DIR = config["CVE_DIR"]
output_dir = config["DB_DIR"]

Path("figure").mkdir(parents=True, exist_ok=True)
Path(output_dir).mkdir(parents=True, exist_ok=True)

if not os.path.isdir(CVE_DIR):
    print("Invalid directory path.")
    exit(2)

# Connect to SQLite database
conn = sqlite3.connect(output_dir + "Fixme.db")
cur = conn.cursor()
print("Connected to SQLite")


def get_language_from_ext(file_path):
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
