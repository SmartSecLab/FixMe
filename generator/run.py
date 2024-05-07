# Generative AI Use Case: Patches Generation

import time
import torch
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    GenerationConfig,
)
from transformers import RobertaTokenizer
from transformers import GenerationConfig
from transformers import AutoTokenizer
from transformers import AutoModelForSeq2SeqLM


# custom functions
from generator.preprocess import load_dataset_from_df
from generator.finetune import fine_tune_model
from generator.prompt import prompt_summary
from generator.evaluate import (
    generate_summaries,
    evaluate_rouge,
    show_original_instruct_summary,
    get_trainable_model_pars,
)
from generator.utility import get_logger


# Setup logger
log = get_logger()

dash_line = "=" * 50

dataset = load_dataset_from_df()

# # ============= Load the model and tokenizer =============
# Load the https://huggingface.co/Salesforce/codet5-base, creating an instance of the `AutoModelForSeq2SeqLM` class with the `.from_pretrained()` method.

# model_name = 'Salesforce/codet5-base'
model_name = "Salesforce/codet5p-6B"
tokenizer = RobertaTokenizer.from_pretrained(model_name, trust_remote_code=True)
# tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name, trust_remote_code=True)
# model = T5ForConditionalGeneration.from_pretrained(model_name)
log.info("Model and Tokenizer loaded successfully!")
log.info(f"Original Model: {model_name}")
log.info(dash_line)

# # ============= Test the Model =============
log.debug("Test the Model")
text = "def greet(user): print(f'hello <extra_id_0>!')"
# text = "def add(a, b): \n int sum= a + b \n return sum"
input_ids = tokenizer(text, return_tensors="pt").input_ids

# simply generate a single sequence
generated_ids = model.generate(input_ids, max_length=8)
log.debug(
    f"Model generated output: {tokenizer.decode(generated_ids[0],skip_special_tokens=True)}"
)
# this prints "{user.username}"
log.info(dash_line)


# Now it's time to explore how well the base LLM summarizes a dialogue without any prompt engineering. **Prompt engineering** is an act of a human changing the **prompt** (input) to improve the response for a given task.
example_indices = [3, 5]
example_index_to_summarize = 2

# ### 2.1 - without Prompt Engineering
log.info(dash_line)
log.info("Generate Patch without Prompt Engineering")
log.info(dash_line)
prompt_summary(
    dataset,
    tokenizer,
    model,
    gen_config=None,
    shot_type=None,
    example_indices=None,
    example_index_to_summarize=example_index_to_summarize,
)


# 3 - Summarize Dialogue with an Instruction Prompt
# You can see that the guesses of the model make some sense, but it doesn't seem to be sure what task it is supposed to accomplish. Seems it just makes up the next sentence in the dialogue. Prompt engineering can help here.
# ## 3 - Summarize Dialogue with an Instruction Prompt
# Prompt engineering is an important concept in using foundation models for text generation. You can check out [this blog](https://www.amazon.science/blog/emnlp-prompt-engineering-is-the-new-feature-engineering) from Amazon Science for a quick introduction to prompt engineering.
# ### 3.1 - Zero Shot Inference with an Instruction Prompt

prompt_summary(
    dataset,
    tokenizer,
    model,
    gen_config=None,
    shot_type="zero",
    example_indices=None,
    example_index_to_summarize=example_index_to_summarize,
)

# TODO: Check prompt template of CodeT5
# ### 3.2 - Zero Shot Inference with the Prompt Template from FLAN-T5


# ## 4 - Summarize Dialogue with One Shot and Few Shot Inference
#
# ### 4.1 - One Shot Inference

example_indices_full = [2]
example_index_to_summarize = 3

prompt_summary(
    dataset,
    tokenizer,
    model,
    gen_config=None,
    shot_type="few",
    example_indices=example_indices_full,
    example_index_to_summarize=example_index_to_summarize,
)

# ### 4.2 - Few Shot Inference

example_indices_full = [2, 3, 4]
example_index_to_summarize = 1

prompt_summary(
    dataset,
    tokenizer,
    model,
    gen_config=None,
    shot_type="few",
    example_indices=example_indices_full,
    example_index_to_summarize=example_index_to_summarize,
)

# generation_config = GenerationConfig(max_new_tokens=50)
# generation_config = GenerationConfig(max_new_tokens=10)
# generation_config = GenerationConfig(max_new_tokens=50, do_sample=True, temperature=0.1)
# generation_config = GenerationConfig(max_new_tokens=50, do_sample=True, temperature=0.5)
generation_config = GenerationConfig(max_new_tokens=50, do_sample=True, temperature=2.0)

prompt_summary(
    dataset,
    tokenizer,
    model,
    gen_config=generation_config,
    shot_type="few",
    example_indices=example_indices_full,
    example_index_to_summarize=example_index_to_summarize,
)

# # # Fine-Tune a Generative AI Model for Dialogue Summarization
log.info("\n\n")
log.info(dash_line)
log.info("========== Fine-Tune the Codet5 Model for Patch Generation =======")
log.info(dash_line)
original_model = AutoModelForSeq2SeqLM.from_pretrained(
    model_name, torch_dtype=torch.bfloat16
)
tokenizer = AutoTokenizer.from_pretrained(model_name)
log.info("Model and Tokenizer loaded successfully!")

# ### 1.2 - Get the Trainable Parameters of the Model
log.info(get_trainable_model_pars(original_model))

# ### 1.3 - Test the Model with Zero Shot Inferencing
prompt_summary(
    dataset,
    tokenizer,
    model,
    gen_config=generation_config,
    shot_type="zero",
    example_indices=example_indices_full,
    example_index_to_summarize=example_index_to_summarize,
)

# generate_summary(dataset, tokenizer, original_model)
output_dir = f"models/instruct-model-{str(int(time.time()))}"

trainer = fine_tune_model(dataset, model, tokenizer, output_dir)


# ### 2.2 - Load the Trained Model
log.info(dash_line)
log.info("Load the Trained Model")
instruct_model = AutoModelForSeq2SeqLM.from_pretrained(
    output_dir, torch_dtype=torch.bfloat16
)

# ### 2.3 - Evaluate the Model Qualitatively (Human Evaluation)
show_original_instruct_summary(
    dataset, tokenizer, original_model, instruct_model, index=example_index_to_summarize
)


# ### 2.4 - Evaluate the Model Quantitatively (ROUGE)
dialogues = dataset["test"][0:4]["dialogue"]
human_baseline_summaries = dataset["test"][0:4]["summary"]

result_csv = "data/patch-gen-training-results.csv"

results = generate_summaries(
    original_model,
    instruct_model,
    tokenizer,
    dialogues,
    human_baseline_summaries,
    result_csv,
)
evaluate_rouge(results)
