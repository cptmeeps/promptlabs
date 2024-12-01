# Project Architecture: Colab-based LLM Prompting Tool

## Introduction

The **Colab-based LLM Prompting Tool** is a modular Python-based application designed to manage and execute Large Language Model (LLM) prompts within Google Colab. It integrates seamlessly with Google Drive for storage and version control, allowing for efficient collaboration and scalability. The tool is built to handle complex prompt chains, making it ideal for tasks that require multiple interactions with LLMs, such as problem-solving, data analysis, and AI-assisted code generation.

## Project Intent and Scope

The primary goal of this project is to provide a flexible and extensible framework for interacting with LLMs in a structured manner. By abstracting prompt management and LLM API interactions, users can focus on designing the logic of their applications without worrying about the underlying complexities. The project supports:

- Modular prompt templates using Jinja2.
- Chain execution defined via YAML configurations.
- Multiple LLM providers with a pluggable architecture.
- Integration with Google Colab and Google Drive.

## Major Components and Modules

### 1. LLM Provider Module (`llm_api.py`)

This module defines the `LLMProvider` abstract base class and its implementations for specific LLM services. It handles interactions with different LLM APIs, allowing for easy integration and switching between providers.

#### Classes

- **`LLMProvider`**: An abstract base class that outlines the necessary methods for any LLM provider implementation.
  - `convert_to_messages`: Converts prompt dictionaries to the provider-specific message format.
  - `generate`: Makes API calls to the LLM service.
  - `parse_response`: Parses the response from the LLM service into plain text.
  - `process_prompt`: Orchestrates the prompt processing workflow.

- **`AnthropicProvider`**: An implementation of `LLMProvider` for the Anthropic API (e.g., Claude models).
  - Utilizes the `anthropic` Python package.
  - Handles system messages and message conversion specific to Anthropic's API.

### 2. Prompt Manager (`prompt/prompt_manager.py`)

Manages the loading, rendering, and composition of prompt templates using Jinja2. It processes templates with provided context variables and prepares the prompts for LLM consumption.

#### Functions

- **`load_prompt_from_file`**: Loads raw prompt content from a file.
- **`compose_prompt`**: Renders templates with context variables and assembles the final prompt chain.

### 3. Chain Manager (`chain/chain_manager.py`)

Executes chains of prompts and actions defined in YAML configuration files. It manages the flow of data and execution steps, calling appropriate functions based on the chain definitions.

#### Features

- **Chain Configuration**: Loads chain definitions from YAML files specifying steps, prompts, and functions.
- **Step Functions**: Registers and executes custom step functions defined within the chain.
- **Context Management**: Maintains a context dictionary to pass data between steps.

### 4. Prompt Templates (`prompt/templates/`)

A collection of template files used to define prompts for various tasks. Templates are written in YAML format and can include Jinja2 templating for dynamic content.

#### Examples

- **`generate_rules.txt`**: A template for generating logical rules based on input and output grids.
- **`solve_puzzle_with_rules.txt`**: Applies generated rules to solve new problems.
- **`summarize.txt`**: Guides the LLM to create summaries based on analyses.

### 5. Chain Templates (`chain/templates/`)

YAML files that define sequences of steps (chains) to be executed by the Chain Manager. Each chain specifies the steps, associated prompts, and functions to be called.

#### Examples

- **`example_chain.yaml`**: Demonstrates a basic analysis and summary chain.
- **`arc_v1.yaml`**: A chain designed to solve ARC (Abstraction and Reasoning Corpus) puzzles.

### 6. Main Script (`main.py`)

The entry point of the application. Currently serves as a placeholder but can be extended to initiate the chain execution or run specific tasks.

## Directory Structure




## Detailed Component Descriptions

### llm_api.py

Defines the `LLMProvider` base class and the `AnthropicProvider` implementation.

- **`LLMProvider`** (Abstract Base Class):
  - **Purpose**: Provides an interface for LLM interactions.
  - **Methods**:
    - `convert_to_messages`
    - `generate`
    - `parse_response`
    - `process_prompt`

- **`AnthropicProvider`**:
  - **Purpose**: Implements the `LLMProvider` methods for Anthropic's API.
  - **Usage**: Initializes with a model name and optional debug mode.

### prompt/prompt_manager.py

Responsible for handling prompt templates.

- **Template Rendering**: Uses Jinja2 to render templates with provided variables.
- **Prompt Composition**: Combines multiple templates into a single prompt chain.
- **Debugging**: Provides detailed debug output when enabled.

### chain/chain_manager.py

Manages the execution of prompt chains.

- **Chain Loading**: Loads chain configurations from YAML files.
- **Step Execution**: Executes each step using registered step functions.
- **Context Handling**: Passes data between steps via a shared context.

### Prompt Templates

Located in `prompt/templates/`, these define the prompts used in chains.

- **Template Structure**: Written in YAML format with roles (`system`, `user`) and contents.
- **Dynamic Content**: Supports Jinja2 templating for dynamic variable substitution.

### Chain Templates

Located in `chain/templates/`, these define the chains of execution.

- **Steps**: Each chain consists of multiple steps with associated prompts and functions.
- **Functions**: Steps can call different functions, such as `process_with_llm`, `generate_rules`, etc.

## How the Pieces Work Together

### Execution Flow

1. **Chain Initialization**: The `ChainManager` loads a chain configuration from a YAML file in `chain/templates/`.
2. **Context Setup**: Initial context variables are set, either from the chain configuration or provided at runtime.
3. **Step Execution**:
   - For each step in the chain:
     1. **Prompt Composition**: The `PromptManager` loads and renders the specified prompt templates using the current context.
     2. **LLM Interaction**: The composed prompt is sent to the LLM via the `LLMProvider`.
     3. **Response Parsing**: The LLM's response is parsed and relevant data is extracted.
     4. **Context Update**: The context is updated with new data from the response.
4. **Result Output**: After all steps are executed, the final results are available in the context.


## Directory Structure

├── README.md
├── requirements.txt
├── llm_api.py
├── main.py
├── prompt/
│ ├── init.py
│ ├── prompt_manager.py
│ └── templates/
│ ├── analyze_text.txt
│ ├── example_combination.txt
│ ├── example_input.txt
│ ├── example_system.txt
│ ├── example.txt
│ ├── example_var.txt
│ ├── generate_rules.txt
│ ├── solve_puzzle_with_rules.txt
│ └── summarize.txt
├── chain/
│ ├── init.py
│ ├── chain_manager.py
│ └── templates/
│ ├── arc_v1.yaml
│ └── example_chain.yaml
├── docs/
│ └── project_architecture.md

## Detailed Component Descriptions

### Example Use Case: Solving an ARC Puzzle

1. **Generate Rules**:
   - **Step**: `generate_rules`
   - **Prompt Template**: `generate_rules.txt`
   - **Function**: `generate_rules`
   - **Action**: LLM generates logical transformation rules based on provided input/output grids.

2. **Solve Puzzle**:
   - **Step**: `solve_puzzle_with_rules`
   - **Prompt Template**: `solve_puzzle_with_rules.txt`
   - **Function**: `solve_puzzle_with_rules`
   - **Action**: Applies the generated rules to a new input grid to produce an output grid.

3. **Evaluate Response**:
   - **Step**: `evaluate_response`
   - **Function**: `evaluate_response`
   - **Action**: Assesses the correctness of the output and updates the context accordingly.

## Requirements and Dependencies

The project relies on several Python packages, specified in `requirements.txt`:

- **`jinja2`**: For template rendering.
- **`pyyaml`**: For loading and parsing YAML files.
- **`anthropic`**: For interfacing with the Anthropic API.
- **`json`** and **`os`**: Standard libraries for JSON handling and operating system interactions.

## Conclusion

The Colab-based LLM Prompting Tool provides a robust framework for managing complex interactions with Large Language Models. By abstracting prompt management, chain execution, and LLM API interactions, it allows developers and researchers to focus on crafting the logic and content of their applications without getting bogged down in infrastructure details.
