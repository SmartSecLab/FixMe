# Generative AI Use Case: Security Patch Generation

In this repository, we explore the application of generative AI for security patch generation. This process involves using large language models to generate patches for security vulnerabilities automatically. Below, we outline the key sections of this repository's README:

## Table of Contents

- Introduction
- Setup
- Generating Patches
- Without Prompt Engineering
- With Instructional Prompts
- Zero-Shot Inference
- Prompt Template from CodeT5
- One-Shot and Few-Shot Inference
- Configuration Parameters

# Structure

| File            | Description                                              |
| --------------- | -------------------------------------------------------- |
| evaluate.py     | Contains code for evaluating the performance of a model. |
| finetune.py     | Script for fine-tuning a model.                          |
| gen-config.yaml | YAML configuration file for generating configurations.   |
| preprocess.py   | Code for preprocessing data.                             |
| prompt.py       | Script for generating prompts.                           |
| run.py          | Main script for running the model.                       |

# Introduction

This repository focuses on using generative AI techniques to automatically generate security patches. We provide methods for generating patches without prompt engineering as well as with different types of instructional prompts.

# Setup

Before generating patches, ensure that you have the necessary dependencies installed. This typically involves installing PyTorch, Hugging Face transformers, and datasets.

# Generating Patches

We offer various methods for generating patches using generative AI models. These methods include:

## Without Prompt Engineering

Here, we generate patches without using any instructional prompts. The model generates patches based solely on the input text.

## With Instructional Prompts

We explore the use of instructional prompts to guide the model in generating patches. This includes:

- Zero-Shot Inference: Providing an instruction prompt to the model without additional training data.

- Prompt Template from CodeT5: Utilizing a predefined prompt template designed for security patch generation from CodeT5 model.

## One-Shot and Few-Shot Inference

In addition to zero-shot inference, we investigate the effectiveness of one-shot and few-shot inference for patch generation:

- One Shot: Providing one example of a security vulnerability and its corresponding patch.
- Few Shot: Offering a few examples of security vulnerabilities and their patches to guide the model.

# Configuration Parameters

We provide information on the configuration parameters used for inference, including model settings and prompt structures.
