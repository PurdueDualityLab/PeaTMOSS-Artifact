from langchain.chat_models import ChatOpenAI
from langchain.chains import create_extraction_chain
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessage, HumanMessage
import time
import json
import argparse
import os

from utils import hf_utils
import prompt

#os.environ["OPENAI_API_KEY"] = keys.OPENAI_API_KEY

openai_api_key = os.environ.get('OPENAI_API_KEY')


with open("metaSchema.json", 'r') as json_file:
    schema = json.load(json_file)

with open("log.txt", 'w') as the_log:
    the_log.write("")
    the_log.close()

parser = argparse.ArgumentParser(description="Python Script with Different Modes")
parser.add_argument("--data", choices = ["input", "groundtruth", "filtered"], required= True, help = "Select to run through input data set, groundtruth set, or filtered model set")
parser.add_argument("--start", type = int, help= "Select which model index to start from in filtered_models.json file")
parser.add_argument("--range", type = int, help= "Select number of models to run through")
args = parser.parse_args()

# load in models
if args.data == "input":
    with open("input.json", 'r') as json_file:
        data = json.load(json_file)
    models_iterable = data
elif args.data == "groundtruth":
    with open("groundTruth.json", 'r') as json_file:
        data = json.load(json_file)
    models_iterable = data.keys()
elif args.data == "filtered":
     
    # make sure they input start and range
    if args.start is None or args.range is None:
        parser.error("for filtered data, starting index and range required.")
    with open("2k_filtered_models.json", 'r') as json_file:
        data = json.load(json_file)

    # get correct models to iterate through wth start and range
    data = list(data.keys())
    start_index = args.start
    end_index = start_index + args.range
    models_iterable = data[start_index: end_index]

def log(text: str):
    with open("log.txt", 'a') as the_log:
        if(type(text) == str):
                the_log.write(text)
        elif(type(text) == dict):
            for key, value in text.items():
                the_log.write(f"{key}: {value}\n")
        the_log.close()

start_time = time.time()
final_result = {}

log(prompt.PREFIX_PROMPT + "\n ")
log(prompt.DOMAIN_PROMPT)
log(prompt.TASK_PROMPT)
log(prompt.LANG_PROMPT)
log(prompt.METADATA_PROMPT  + "\n")


for index, model in enumerate(models_iterable):
    model_result = {}
    try:
        card = hf_utils.load_card(model)
        model_result["domain"], model_result["model_task"] = hf_utils.get_domain_and_task(model)
        model_result["frameworks"]= hf_utils.get_frameworks(model)
        model_result["libraries"]= hf_utils.get_libraries(model)


        pre_schema = {}
        extra_prompt =""
        
        # checks need to add domain as metadata for when task not pre-processed
        if not len(model_result["domain"]):
            domain_schema = {"domain": {"items": {"type": "string"}}}
            pre_schema = {**pre_schema, **domain_schema}
            extra_prompt += prompt.DOMAIN_PROMPT

        # checks need to add task as metadata for when task not pre-processed
        if not len(model_result["model_task"]):
            task_schema = {"model_task": {"items": {"type": "string"}}}
            pre_schema = {**pre_schema, **task_schema}
            extra_prompt += prompt.TASK_PROMPT
            
        # checks need to add language as metadata for NLPs
        is_nlp = "natural-language-processing" in model_result["domain"]
        if is_nlp:
            lang_schema = {"language": {"items": {"type": "string"}}}
            pre_schema = {**pre_schema, **lang_schema}
            extra_prompt += prompt.LANG_PROMPT

        data_schema = {"properties": {**pre_schema, **schema["extract_metadata"]}}

        
        # set chatbot as gpt-4-turbo
        chatbot = ChatOpenAI(temperature = 0.1, model = "gpt-4-1106-preview")
        
        # extraction chat prompt, system msg being rules, first human prompt being model card, and result will be first assistant response
        extraction_prompt = ChatPromptTemplate.from_messages(
            [
                #f-string to add metadata prompt for language prompt
                SystemMessage(content = f"{prompt.PREFIX_PROMPT}\n{extra_prompt}{prompt.METADATA_PROMPT}"),
                HumanMessage(content = card)
            ]
        )

        # putting schema, llm, and prompt together
        chain = create_extraction_chain(schema = data_schema, llm = chatbot, prompt = extraction_prompt)

        # running the chain, args are to fill in f-string in extraction_prompt
        extraction_result = chain.run({
            "domain": model_result["domain"],
            "model": model
            })

        # normally outputs as dict in list [{...}] but sometimes outputs as list {...}, this is a way to catch both
        # and combine it with pre-processed metadata
        if type(extraction_result) == list:
            model_result = {**model_result,**extraction_result[0]}
        if type(extraction_result) == dict:
            model_result = {**model_result,**extraction_result}

        final_result[model] = model_result

    except Exception as e:
        final_result[model] = str(e)
        log(model + ": " + str(e) + "\n")
        
    with open(f"result_{args.start}_{args.range}.json", "w") as json_file:
        json.dump(final_result, json_file, indent = 4)

end_time = time.time()
log(f"total elapsed time: {int((end_time - start_time)/3600)} hours {int((end_time-start_time)/60%60)} minutes {int(end_time-start_time)%60} seconds")
