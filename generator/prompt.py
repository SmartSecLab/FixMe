# Generative AI Use Case: Patches Generation

from transformers import (
    GenerationConfig,
)
from transformers import GenerationConfig

# custom functions
from generator.utility import get_logger


# Setup logger
log = get_logger()

dash_line = "-" * 20


def show_few_examples(dataset, num_examples=2):
    # Print the first few dialogues and summaries
    log.info("Examples in the dataset:")
    example_indices = [2, 4]
    # dash_line = '=' * 50

    for i, index in enumerate(example_indices):
        log.info(dash_line)
        log.info(f"Example {i + 1}")
        log.info(dash_line)
        log.info("Vulnerable code:")
        log.info(dataset["test"][index]["dialogue"])
        log.info(dash_line)
        log.info("BASELINE PATCH:")
        log.info(dataset["test"][index]["summary"])
        log.info(dash_line)
        log.info()


# -


def zero_prompt(dataset, index=2):
    dialogue = dataset["test"][index]["dialogue"]
    return f"""
    Vulerable program code:

    {dialogue}

    Patch of the program is:
    """


def one_few_prompt(dataset, example_indices, example_index_to_summarize):
    """Construct the prompt to perform one shot inference:"""
    prompt = ""
    for index in example_indices:
        dialogue = dataset["test"][index]["dialogue"]
        summary = dataset["test"][index]["summary"]

        # The stop sequence '{summary}\n\n\n' is important for FLAN-T5. Other models may have their own preferred stop sequence.
        prompt += f"""
                    Vulerable C program:

                    {dialogue}

                    Patch of the program is:

                    {summary}

                    """

    dialogue = dataset["test"][example_index_to_summarize]["dialogue"]

    prompt += f"""
                Vulerable program code:

                {dialogue}

                Patch of the program is:
                """

    return prompt


def without_prompt(dataset, index=2):
    dialogue = dataset["test"][index]["dialogue"]
    return dialogue


def generate_summary(prompt, tokenizer, model, gen_config=None):
    """
    This line defines a function called generate_summary that takes four parameters:
    prompt: The text to be summarized.
    tokenizer: A tokenizer object that converts text into numerical tokens, usually to be processed by a model.
    model: A language model that generates text. This could be something like GPT (Generative Pre-trained Transformer) model.
    gen_config: Optional configurations for the text generation process.
    """
    inputs = tokenizer(prompt, return_tensors="pt")
    if gen_config is None:
        gen_config = GenerationConfig(max_length=100)

    output = tokenizer.decode(
        model.generate(
            inputs["input_ids"],
            max_new_tokens=100,
            generation_config=gen_config,
        )[0],
        skip_special_tokens=True,
    )
    return output


def prompt_summary(
    dataset,
    tokenizer,
    model,
    gen_config=None,
    shot_type="zero",
    example_indices=None,
    example_index_to_summarize=2,


):
    dash_line = "-" * 25
    if shot_type == "zero":
        prompt = zero_prompt(dataset, example_index_to_summarize)
    elif shot_type == "one_few":
        prompt = one_few_prompt(dataset, example_indices,
                                example_index_to_summarize)
    else:
        prompt = without_prompt(dataset, example_index_to_summarize)

    prompt = zero_prompt(dataset)

    summary = dataset["test"][example_index_to_summarize]["summary"]
    output = generate_summary(prompt, tokenizer, model, gen_config)

    dash_line = "-".join("" for x in range(100))
    log.info(dash_line)
    log.info(f"INPUT PROMPT:\n{prompt}")
    log.info(dash_line)
    log.info(f"BASELINE PATCH:\n{summary}\n")
    log.info(dash_line)
    log.info(f"MODEL GENERATION - ZERO SHOT:\n{output}")
