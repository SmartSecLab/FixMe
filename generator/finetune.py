
# Fine-tune the model on the dataset

# ## 2 - Perform Full Fine-Tuning
import time
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, GenerationConfig, TrainingArguments, Trainer
from transformers import RobertaTokenizer, T5ForConditionalGeneration


def tokenize_function(example, tokenizer):
    start_prompt = 'Summarize the following conversation.\n\n'
    end_prompt = '\n\nSummary: '
    prompt = [start_prompt + dialogue +
              end_prompt for dialogue in example["dialogue"]]
    example['input_ids'] = tokenizer(
        prompt, padding="max_length", truncation=True, return_tensors="pt").input_ids
    example['labels'] = tokenizer(
        example["summary"], padding="max_length", truncation=True, return_tensors="pt").input_ids

    return example


def fine_tune_model(dataset, model, tokenizer, output_dir):
    # The dataset actually contains 3 diff splits: train, validation, test.
    # The tokenize_function code is handling all data across all splits in batches.
    tokenized_datasets = dataset.map(
        lambda example: tokenize_function(example, tokenizer), batched=True)
    tokenized_datasets = tokenized_datasets.remove_columns(
        ['id', 'topic', 'dialogue', 'summary',])

    # # Filter the dataset to keep only a few examples for training
    # tokenized_datasets = tokenized_datasets.filter(
    #     lambda example, index: index % 100 == 0, with_indices=True)

    print(f"Shapes of the datasets:")
    print(f"Training: {tokenized_datasets['train'].shape}")
    print(f"Validation: {tokenized_datasets['validation'].shape}")
    print(f"Test: {tokenized_datasets['test'].shape}")
    print(tokenized_datasets)

    training_args = TrainingArguments(
        output_dir=output_dir,
        learning_rate=1e-5,
        num_train_epochs=2,
        weight_decay=0.01,
        logging_steps=1,
        max_steps=1
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets['train'],
        eval_dataset=tokenized_datasets['validation']
    )

    trainer.train()

    # Save the trained model
    trainer.save_model(f'models/instruct_model-{output_dir}')

    return trainer
