# Fine-tune the model on the dataset
import yaml
from transformers import (
    TrainingArguments,
    Trainer,
)

# custom functions
from generator.utility import get_logger


# Setup logger
log = get_logger()

dash_line = "=" * 50


def load_config(config_path):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config


config = load_config("generator/gen-config.yaml")


def tokenize_function(example, tokenizer):
    start_prompt = "Summarize the following conversation.\n\n"
    end_prompt = "\n\nSummary: "
    prompt = [start_prompt + dialogue + end_prompt for dialogue in example["dialogue"]]
    example["input_ids"] = tokenizer(
        prompt, padding="max_length", truncation=True, return_tensors="pt"
    ).input_ids
    example["labels"] = tokenizer(
        example["summary"], padding="max_length", truncation=True, return_tensors="pt"
    ).input_ids

    return example


def fine_tune_model(dataset, model, tokenizer, output_dir):
    # The dataset actually contains 3 diff splits: train, validation, test.
    # The tokenize_function code is handling all data across all splits in batches.
    tokenized_datasets = dataset.map(
        lambda example: tokenize_function(example, tokenizer), batched=True
    )
    tokenized_datasets = tokenized_datasets.remove_columns(
        [
            "id",
            "topic",
            "dialogue",
            "summary",
        ]
    )

    # # Filter the dataset to keep only a few examples for training
    # tokenized_datasets = tokenized_datasets.filter(
    #     lambda example, index: index % 100 == 0, with_indices=True)

    log.info(f"Shapes of the datasets:")
    log.info(f"Training: {tokenized_datasets['train'].shape}")
    log.info(f"Validation: {tokenized_datasets['validation'].shape}")
    log.info(f"Test: {tokenized_datasets['test'].shape}")
    log.info(tokenized_datasets)

    # training_args = TrainingArguments(
    #     output_dir=output_dir,
    #     learning_rate=1e-5,
    #     num_train_epochs=2,
    #     weight_decay=0.01,
    #     logging_steps=1,
    #     max_steps=1
    # )
    training_args = TrainingArguments(
        output_dir=output_dir,
        learning_rate=float(config["fine_tuning"]["learning_rate"]),
        num_train_epochs=config["fine_tuning"]["num_train_epochs"],
        weight_decay=config["fine_tuning"]["weight_decay"],
        logging_steps=config["fine_tuning"]["logging_steps"],
        max_steps=config["fine_tuning"]["max_steps"],
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
    )

    trainer.train()

    # Save the trained model
    trainer.save_model(output_dir)
    log.info(dash_line)
    log.info("Fine-Tuning Completed!")
    log.info(f"Model saved to {output_dir}")
    log.info(dash_line)

    return trainer
