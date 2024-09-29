# InterIntent

This repository contains the code for the paper: **"InterIntent: Investigating Social Intelligence of LLMs via Intention Understanding in an Interactive Game Context"**. You can find the paper here: [arXiv link](https://arxiv.org/abs/2406.12203).

InterIntent is a framework for evaluating agents in social settings, built on top of [ChatArena](https://github.com/Farama-Foundation/chatarena), using the game *Avalon* as the testing environment.

## Configuration

The project uses the `config.yml` file in the root directory to specify model and various paths for running the project. The default configurations are given below:

```yaml
model_name: "gpt-3.5-turbo-0125"
model_folder_name: "gpt-3-5-turbo-0125"
is_openai_model: true

base_output_path: "output"

output_game_folder: ${base_output_path}/${model_folder_name}/games
structured_context_save_path: ${base_output_path}/${model_folder_name}/evaluation
hallucination_detection_save_path: ${base_output_path}/${model_folder_name}/evaluation/hallucination_detection
annotated_data_save_path: ${base_output_path}/${model_folder_name}/annotated

evaluation_phase: "first_order" # first_order for intent guessing, other options - intent_summarization, hallucination_detection
model_evaluation_save_path: ${base_output_path}/${model_folder_name}/evaluation
```

## Running Experiments

To run a game experiment, navigate to the root of the repository and execute:
```bash
python avalon.py
```

The model used for the experiment is defined in the `config.yml` as parameter `model_name`. If, the model is from OpenAI, we set the parameter `is_openai_model` to true. Currently, we have support only for llama2 apart from OpenAI models.

The script runs the game for a maximum of 5 rounds and terminates when a team wins. The game output is saved in the directory specified by `output_game_folder` in the configuration file.

Experiments run as part of the research are stored in:
- `output/gpt-3-5-turbo-0125`
- `output/gpt-4`

## Post-Experiment Processing and Evaluation

Scripts for processing game files for annotation and evaluation of annotated files are located in the `scripts` directory.

To clean game files for annotation, run the following:
```bash
python scripts/process_conversation_files.py
```

Post annotation, annotated games should be stored under `annotated_data_save_path` folder defined in `config.yml`
Next, after annotation run
```bash
python scripts/process_conversation_reconsider_team.py
```
The above adds additional column for secondary rounds(rounds where previous vote fail and leader had to change for team selection in the Avalon game) identifier.

### Generating Structured Context Files
The scripts given below are used to generate structured prompts given the annotated game files.
Parameters - `annotated_data_save_path` contains the data to be used for structured context generation, `structured_context_save_path` should specify the path where the generated data is saved for intent guessing and summarization. `hallucination_detection_save_path` should specify where the generated data is saved for hallucination detection.
- **For intent guessing and summarization**: 
  ```bash
  python scripts/generate_structured_context_data.py
  ```
- **For intent guessing with perspective prompts**: 
  ```bash
  python scripts/generate_structured_context_perspective_data.py
  ```
- **For hallucination detection**: 
  ```bash
  python scripts/generate_hallucination_detection_data.py
  ```

### Evaluation with Structured Context data
To run the evaluation for intent guessing, summarization and hallucination detection, use `avalon_evaluation.py`.
This file prompts the LLM with a given structured context and the corresponding task (`intent summarization`, `intent guessing`, or `hallucination detection`) as specified in the `evaluation_phase` setting of the `config.yml` file.

The response is stored in the directory specified by `model_evaluation_save_path` in the configuration file, which by default is:
```
output/${model_folder_name}/evaluation
```
