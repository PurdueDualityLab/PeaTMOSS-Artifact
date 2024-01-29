METADATA_PROMPT = {
    "datasets": "What datasets were used to train the model (include link if possible)", # eval: 
    "license": "What is the license", # eval: 
    "github": "What links to github repositories are available and what these links are for", # eval: 
    "paper": "What is the research paper associated to this model", # eval: 
    "upstream_model": "What is the upstream model of this model", # eval:
    "parameter_count": "What are the number of parameters (#params) this model is trained on", # eval: 
    "hyper_parameters": "What are the values of some hyper parameters (parameters that control the learning process of the model) of this model.", # eval: 
    "evaluation": "What is the evalutaion of the model. What evaluation metrics where used, and what are the results (include whole table if possible)", # eval: 
    "hardware": "What hardware was used to train this model", # eval: 
    "limitation_and_bias": "What are the limitations and biases of the model", # eval: 
    "demo": "Find a form of demo for the model could be a link, code snippet or short paragraph", # eval: 
    "input_format": "What is the format of the data used as input for the model", # eval: 
    "output_format": "What is the format of the data used as output of the model", # eval: 
    "input_preprocessing": "What is the input preprocessing of this model", # eval: 
    "input_size": "What is the image input size",  # eval:  
    "max_sequence_length": "What is the max sequence length of this NLP model", # eval: 
    "vocabulary_size": "What is the vocabulary size of this NLP model", # eval: 
    "sample_rate": "What is the sample rate of this model", # eval: 
    "agent": "What is the agent of this reinforcement learning model", #eval:
    "training_environment": "What is the training environment of this reinforcement learning model", #eval:
    "SB3": "Is SB3 used in this reinforcement learning model", #eval:
}

PREFIX_PROMPT = \
    "Given metadata information of huggingface {model_type} model : {model}, extract the properties of ONE single entity mentioned in the 'information_extraction' function.\n \
    Extraction rules: \n \
    - rule 1: Adhere strictly to the schema structure in 'information_extraction'\n \
    - rule 2: If a property is not present but is required in the function parameters, output "" instead\n \
    - rule 3: If a property is not present and is not required in the function parameters, do not include it in the output\n \
    - rule 4: Only extract one item for 'info' in 'information_extraction' function \n \
"    
EXTRACTION_PROMPT =\
    "Extraction rules for specific metadata: \n \
    - datasets: only return dataset used to train or finetune model, not the upstream model of the model\n \
    - github: extract github link of this model (only return the github link)\n \
    - paper: if a research paper was written, extract arxiv research paper link (only return the url of the paper)\n \
    - parameter_count: The number of parameters the model was trained on, sometimes represented in the form #params\n \
    - upstream_model: provide huggingface model ID of upstream model\n \
    - hyper_parameters: extract possible hyperparameters\n \
    - evaluation: extract evaluation metric/tasks and their respective evaluation results\n \
    - hardware: extract any hardware used to train the model\n \
    - limitation_and_biases: extract a short summary of limitation and biases of the model\n \
    - demo: extract any links, code snippets, or small paragraphs on how to use the model\n \
    - input_format: extract the input format/requirement for this model\n \
    - output_format: extract the output format of this model\n \
"