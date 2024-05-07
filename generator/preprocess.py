# Generative AI Use Case: Patches Generation

import pandas as pd
from datasets import Dataset, DatasetDict
import pandas as pd
import sqlite3

# custom functions
from generator.utility import get_logger


# Setup logger
log = get_logger()

debug = True
db_file = "/Users/guru/research/FixMe/data/FixMe-v1.db"


def load_df_from_sqlite():
    """Load the dataset from the SQLite database"""
    conn = sqlite3.connect(db_file)

    if debug:
        df = pd.read_sql_query(
            "SELECT * FROM hunk_collection LIMIT 500;", conn)
    else:
        df = pd.read_sql_query("SELECT * FROM hunk_collection;", conn)

    log.info(f"Dataset shape: {df.shape}")

    df = df[df.programming_language.isin(["C", "C++"])].reset_index(drop=True)
    df = df[["code_before", "code_after"]]

    return df


def load_dataset_from_df():
    """Load the dataset and split it into train, val, and test sets"""
    df = load_df_from_sqlite()
    total_rows = len(df)
    train_size = int(total_rows * 0.8)
    val_size = int(total_rows * 0.1)

    train_df = df.iloc[:train_size]
    validation_df = df.iloc[train_size: train_size + val_size]
    test_df = df.iloc[train_size + val_size:]

    def df_to_dicts(df):
        """Convert DataFrame to list of dictionaries"""
        return [
            {
                "id": i,
                "dialogue": row["code_before"],
                "summary": row["code_after"],
                "topic": "",  # Optional field
            }
            for i, row in df.iterrows()
        ]

    # Create Dataset objects
    train_dataset = Dataset.from_dict(
        {
            "id": list(train_df.index),
            "dialogue": train_df["code_before"],
            "summary": train_df["code_after"],
            "topic": [""] * len(train_df),
        }
    )
    validation_dataset = Dataset.from_dict(
        {
            "id": list(validation_df.index),
            "dialogue": validation_df["code_before"],
            "summary": validation_df["code_after"],
            "topic": [""] * len(validation_df),
        }
    )
    test_dataset = Dataset.from_dict(
        {
            "id": list(test_df.index),
            "dialogue": test_df["code_before"],
            "summary": test_df["code_after"],
            "topic": [""] * len(test_df),
        }
    )

    # Create DatasetDict with the desired format
    dataset = DatasetDict(
        {"train": train_dataset, "validation": validation_dataset, "test": test_dataset}
    )
    log.info(f'Train shape: {dataset["train"].shape}')
    log.info(f'Validation shape: {dataset["validation"].shape}')
    log.info(f'Test shape: {dataset["test"].shape}')
    return dataset
