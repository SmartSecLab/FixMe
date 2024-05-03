
# Generative AI Use Case: Patches Generation

import numpy as np
import pandas as pd
import evaluate
import time
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, GenerationConfig, TrainingArguments, Trainer
from transformers import RobertaTokenizer, T5ForConditionalGeneration
from datasets import Dataset, DatasetDict
from transformers import GenerationConfig
from transformers import AutoTokenizer
from transformers import AutoModelForSeq2SeqLM
from datasets import load_dataset
import pandas as pd
import nltk
import sqlite3
from nltk.translate.bleu_score import sentence_bleu

debug = True

conn = sqlite3.connect('/Users/guru/research/FixMe/data/FixMe-v1.db')

if debug:
    df = pd.read_sql_query("SELECT * FROM hunk_collection LIMIT 500;", conn)
else:
    df = pd.read_sql_query("SELECT * FROM hunk_collection;", conn)

print(f'Dataset shape: {df.shape}')

df = df[df.programming_language.isin(
    ['C', 'C++'])].reset_index(drop=True)
df = df[['code_before', 'code_after']]


def load_dataset_from_df():
    """ Load the dataset from the DataFrame and split it into train, validation, and test sets
    """
    total_rows = len(df)
    train_size = int(total_rows * 0.8)
    val_size = int(total_rows * 0.1)

    train_df = df.iloc[:train_size]
    validation_df = df.iloc[train_size:train_size + val_size]
    test_df = df.iloc[train_size + val_size:]

    def df_to_dicts(df):
        """Convert DataFrame to list of dictionaries"""
        return [
            {
                'id': i,
                'dialogue': row['code_before'],
                'summary': row['code_after'],
                'topic': '',  # Optional field
            }
            for i, row in df.iterrows()
        ]

    # Create Dataset objects
    train_dataset = Dataset.from_dict({'id': list(
        train_df.index), 'dialogue': train_df['code_before'], 'summary': train_df['code_after'], 'topic': [''] * len(train_df)})
    validation_dataset = Dataset.from_dict({'id': list(
        validation_df.index), 'dialogue': validation_df['code_before'], 'summary': validation_df['code_after'], 'topic': [''] * len(validation_df)})
    test_dataset = Dataset.from_dict({'id': list(
        test_df.index), 'dialogue': test_df['code_before'], 'summary': test_df['code_after'], 'topic': [''] * len(test_df)})

    # Create DatasetDict with the desired format
    dataset = DatasetDict({
        'train': train_dataset,
        'validation': validation_dataset,
        'test': test_dataset
    })
    print(f'Train shape: {dataset["train"].shape}')
    print(f'Validation shape: {dataset["validation"].shape}')
    print(f'Test shape: {dataset["test"].shape}')
    return dataset
