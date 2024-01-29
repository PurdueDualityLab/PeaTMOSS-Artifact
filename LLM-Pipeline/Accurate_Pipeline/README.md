# About

The repository contains the accurate (GPT-4-turbo) pipeline to extract metadata from, the models to be extracted from, the prompts and schema used to define metadata format and requirements. 

# Schema

The schema contains most of the metadata to be extracted of a model card. It is split into pre-processed metadata schema and extracted metadata schema. Pre-processed metadata schema includes schema for domain, tasks, libraries and frameworks, from which tasks, libraries, and frameworks could be retrieved from huggingface api model tags. The domain could then be gotten through domain-task mapping. The extracted metadata schema contains datasets, license, gihub repo, paper, base model, parameter count, hardware, carbon emitted, hyper parameter, evaluation, limitation and bias, demo, grant, and input/output format. If the domain of the model is found to be a NLP during pre-processing, we also add language to the extracted metadata schema to be extracted by the LLM.


# Prompt 

The LLM we are using is a ChatGPT-4-turbo. It being a conversational model, means that we can set system messages and human messages. For system message, we input a prompt consisting of two main sections, the prefix prompt and the metadata prompt. The prefix prompt provides the domain and model name, setting extraction rules and schema adherence, with empty properties for absent document elements. The metadata prompt defines what we expect of each metadata extracted and enforces the format that we want extracted. For the human message that follows, we input the whole model card into ChatGPT-4-turbo, leaving the assistant response as the output result. 

# Pipeline

In the accurate pipeline, we utilize Langchain to chain the components together. In this case, we chain the LLM with a desired output schema and our parameterized prompts. 
The accurate pipeline, utilizing GPT-4-turbo, has a substantial improvement on addressing the token limit issue, along with enhanced performance in data extraction. An analysis of the token count across all model cards revealed that their lengths fell within the new token limit of GPT-4-turbo (128,000 tokens).


# How to use

## Set up environment

The environment is stroed in env.yml file, and could be set up through conda by,

conda env create -f environment.yml

and 

conda activate ptm_env

# Extraction

To get started choose between running models in the input.json file,

python pipeline.py --data input

running models in groundtruth.json file, 

python pipeline.py --data groundtruth

or running through 2k_filtered_models.json file

python pipeline.py --data filtered --start <start_index> --range <range_of_models_to_run_through>