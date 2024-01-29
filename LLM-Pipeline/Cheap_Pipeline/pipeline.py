import huggingface_hub
import openai
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.chat_models import ChatOpenAI
from langchain.chains import create_extraction_chain
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessage, HumanMessagePromptTemplate
import time
import json
import argparse
import asyncio
import sys
import os

import prompt

openai_api_key = os.environ.get('OPENAI_API_KEY')

with open("metaSchema.json", 'r') as json_file:
    schema = json.load(json_file)

with open("log.txt", 'w') as the_log:
    the_log.write("")
    the_log.close()

parser = argparse.ArgumentParser(description="Python Script with Different Modes")
parser.add_argument("--data", choices = ["input", "filtered"], required= True, help = "Select to run through input data set or filtered model set")
parser.add_argument("--start", type = int, help= "Select which model index to start from in filtered_models.json file")
parser.add_argument("--range", type = int, help= "Select number of models to run through")
args = parser.parse_args()

#loads in models
if args.data == "input":
    with open("input.json", 'r') as json_file:
        data = json.load(json_file)
elif args.data == "groundtruth":
    with open("groundTruth.json", 'r') as json_file:
        data = json.load(json_file)
    models_iterable = data.keys()
elif args.data == "filtered":
    
    # make sure they input start and range
    if args.start is None or args.range is None:
        parser.error("for filtered data, starting index and range required.")
    with open("filtered_models.json", 'r') as json_file:
        data = json.load(json_file)

def load_card(model_name: str) -> str:

    try:
        card = huggingface_hub.ModelCard.load(model_name)
    except huggingface_hub.utils._errors.RepositoryNotFoundError:
        print(f"{model_name} repo not found\n")
        #card.data = tags
        #card.text card
        #cald.content tags+cards
    return ("#tags\n\n" + card.content)
    
def get_type_and_task(model_name: str) -> (str,str):
    model_info = huggingface_hub.hf_api.model_info(model_name)
    tags = model_info.tags
    model_task = None
    model_type = None

    tasks = {
    "multimodal":["feature-extraction", "text-to-image", "image-to-text", "text-to-video", "visual-question-answering", "document-question-answering", "graph-machine-learning"],
    "computer-vision":["depth-estimation", "image-classification", "object-detection", "image-segmentation", "image-to-image", "unconditional-image-generation", "video-classification", "zero-shot-image-classification"],
    "natural-language-processing":["text-classification", "token-classification", "table-question-answering", "question-answering", "zero-shot-classification", "translation", "summarization", "conversational", "text-generation", "text2text-generation", "fill-mask", "sentence-similarity"], 
    "audio":["text-to-speech", "automatic-speech-recognition", "audio-to-audio", "audio-classification", "voice-activity-detection"],
    "tabular":["tabular-classification", "tabular-regression"],
    "reinforcement-learning":["reinforcement-learning", "robotics"]
    }

    for tag in tags:
        for key in tasks.keys():
            if tag in tasks[key]:
                model_type = key
                model_task = tag
    return (model_type, model_task)

def get_frameworks(model_name: str) -> list:
    model_info = huggingface_hub.hf_api.model_info(model_name)
    tags = model_info.tags

    frameworks = ["pytorch", "tensorflow", "jax", "transformers", "tensorboard", "diffusers", "stable-baselines3", "safetensors", "peft", "onnx", 
                  "ml-agents", "sentence-transformers", "timm", "sample-factory", "keras", "adapter-transformers", "flair", "spacy", "espnet", 
                  "transformers.js", "fastai", "core-ml", "rust", "nemo","joblib","scikit-learn","fasttext","speechbrain","paddlepaddle","openclip",
                  "bertopic", "fairseq", "openvino", "graphcore", "stanza", "tf-lite", "asteroid", "paddlenlp", "allennlp", "spanmarker", "habana", 
                  "pythae", "pyannote.audio" ]

    return list(set(tags) & set(frameworks))

def get_data_schema(model_type: str, model_tasks: list, frameworks: list) -> (dict, dict):
    general_schema = dict(schema["general_metadata"])
    general_schema.pop("model_type")
    general_schema.pop("model_tasks")
    general_schema.pop("frameworks")

    pre_extraction_data = {"model_type": model_type, 
                           "model_tasks": model_tasks,
                           "frameworks": frameworks
                           }

    if model_type:
        task_specific_schema = dict(schema["task_specific_metadata"][model_type])
        metadata_schema = {
            "properties": {**general_schema, **task_specific_schema}
            }
        return (pre_extraction_data, metadata_schema)
    return (pre_extraction_data, {"properties": general_schema})

def pretty_print_docs(docs, metadata):
    return f"{'-' * 20} {metadata} {'-' * 20}\n\n" + f"\n{'-' * 30}\n".join([f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)]) + "\n\n"

def log(text: str):
    with open("log.txt", 'a') as the_log:
        the_log.write(text)
        the_log.close()

def log_list(content: str):
    line_width = 100
    lines = [content[i:i+line_width] for i in range(0, len(content), line_width)]
    with open("log.txt", "a") as file:
        for line in lines:
            file.write(f"{line.ljust(line_width)} \n")
        file.close()
    

log("Metadata Prompt: \n\n " + str(prompt.METADATA_PROMPT) + "\n")
log("Extraction Prompt: \n\n" + str(prompt.EXTRACTION_PROMPT) + "\n")

if args.data == "input":
    models_iterable = data

if args.data == "filtered":
    data = data.keys()
    start_index = args.start
    end_index = start_index + args.range
    models_iterable = data[start_index: end_index]

start_time = time.time()
result = {}

#change between filtered_models and input_models
for model in models_iterable:
    try:
        card = load_card(model)
        card = card.replace('"', "'")
        log(f"\n#####################{model}########################\n\n")
        model_type, model_tasks = get_type_and_task(model)
        frameworks = get_frameworks(model)
        pre_extract, data_schema = get_data_schema(model_type, model_tasks, frameworks)

        headers_to_split_on = [("#", "header 1"), ("##", "header 2"), ("###", "header 3")]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on = headers_to_split_on)
        md_header_splits = markdown_splitter.split_text(card)
        #print(md_header_splits)

        vector_store = FAISS.from_documents(md_header_splits, OpenAIEmbeddings(allowed_special={'<|endoftext|>', '<|prompter|>', '<|assistant|>'}))
        llm = OpenAI(temperature = 0)
        compressed_docs = ""
        for metadata in data_schema["properties"]:
            retriever = vector_store.as_retriever(search_kwargs = {"k": 3})
            retriever_prompt = prompt.METADATA_PROMPT[metadata]
            # docs = list of doc objects
            docs = retriever.get_relevant_documents(retriever_prompt)
            compressor = LLMChainExtractor.from_llm(llm)
            compression_retriever = ContextualCompressionRetriever(base_compressor = compressor, base_retriever = retriever)
            compressed_docs += pretty_print_docs(compression_retriever.get_relevant_documents(retriever_prompt + f" (Do not remove keyword \"{metadata}\" in compressed doc)"), metadata)
        log(compressed_docs)

        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content = (prompt.PREFIX_PROMPT + prompt.EXTRACTION_PROMPT)),
                HumanMessagePromptTemplate.from_template("{documents}"),
            ]
        )

        chatbot = ChatOpenAI(temperature = 0.1, model = "gpt-3.5-turbo")
        chain = create_extraction_chain(schema = data_schema, llm = chatbot, prompt = prompt_template)

        extraction_result = chain.run({
            "model_type": model_type,
            "model": model,
            "documents": compressed_docs
            })

        
        log_list("\n" + str(extraction_result))
        if type(extraction_result) == list:
            result[model] = {**pre_extract, **extraction_result[0]}
        else:
            result[model] = {**pre_extract, **extraction_result}

    #exceed token limit of 4096
    except Exception as e:

        log(f"\nERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n {str(e)} \n")
        result[model] = str(e)
        
    with open("result.json", "w") as json_file:
        json.dump(result, json_file, indent = 4)

end_time = time.time()
log(f"total elapsed time: {int((end_time - start_time)/3600)} hours {int((end_time-start_time)/60%60)} minutes {int(end_time-start_time)%60} seconds")
