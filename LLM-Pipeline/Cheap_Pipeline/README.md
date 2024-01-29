# About

The repository contains the cheap (GPT-3.5-turbo) pipeline to extract metadata from, the models to be extracted from, the prompts and schema used to define metadata format and requirements. 

# Schema

The schema contains most of the metadata to be extracted of a model card. It is split into general metadata schema and specific metadata schema. General metadata include metadata that are applicable to all models regardless of their domain. The general metadata schema includes metadata such as domain, tasks, libraries and frameworks that we can retrieve from  huggingface api model tags. The domain could then be gotten through domain-task mapping. The task specific metadata are metadata exclusive to different domains. These metadata are appended at the end of the general metadata schema depending on which domain the model belongs to. 


# Prompt 

The LLM we are using is a ChatGPT-3.5-turbo. It being a conversational model, means that we can set system messages and human messages. For system message, we input a prompt consisting of two main sections, the prefix prompt and the metadata prompt. The prefix prompt provides the domain and model name, setting extraction rules and schema adherence, with empty properties for absent document elements. The extraction prompt defines what we expect of each metadata extracted and enforces the format that we want extracted. For the human message that follows, we input the whole model card into ChatGPT-3.5-turbo, leaving the assistant response as the output result. There is also a metadata prompt that is used during the RAG process to compress our model card documents.

# Pipeline

In the cheap pipeline, we utilize Langchain to enable RAG framework to reduce number of tokens inputed into the LLM. The pipeline consists of transforming, retrieving and compressing, and extracting. First we transform the model card into document objects. A document object contains text content and the sub-section headers that the text belongs to, this way we can disect the model cards into smaller documents while maintaining markdown structure. The documents are stored in FAISS vectorstores. Based on individual metadata prompts, we retrieve documents associated with the metadata using OpenAI-Embeddings and compress the documents into smaller text strings using InstructGPT to fit under the 4096 token limit. After retrieval and compression, the retrieved and compressed information are appended together and inputed into GPT-3.5-turbo as the human message, with the assistnt message as the result.


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