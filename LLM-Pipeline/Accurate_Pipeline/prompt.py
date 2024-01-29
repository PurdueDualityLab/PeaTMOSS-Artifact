PREFIX_PROMPT = \
"Given model card of Huggingface {domain} model : {model} fill in the following model schema structure in 'information_extraction' function\n\
Rules:\n \
- rule 1: Adhere strictly to the schema structure\n \
- rule 2: If you are confident a property is not present in the documents, leave as empty string in the schema\n\
"


METADATA_PROMPT = \
"\
- datasets: return dataset used to train or finetune model, not the upstream model of the model\n \
- license: return this model's license\n \
- github_repo: return github repository of this model\n \
- paper: return research paper of this model\n \
- base_model: return huggingface model ID of upstream model\n \
- parameter_count: return the number of parameters, represented with \"M\", \"B\", and \"T\" as million, billion, and trillion\n \
- hardware: extract any hardware associated with the model\n \
- carbon_emitted: extract the carbon emissions amount of the model\n \
- hyper_parameters: extract possible hyperparameters\n \
- evaluation: extract evaluation metric/tasks and their respective evaluation results or a url to evaluation results\n \
- limitation_and_biases: extract a short summary of limitation and biases of the model\n \
- demo: extract any links, code snippets, or small paragraphs on how to use the model\n \
- grant: extract the grant/sponsors of this model\n \
- input_format: extract the input format/requirement for this model\n \
- output_format: extract the output format of this model\n \
"

DOMAIN_PROMPT = "- domain: multimodal, computer-vision, natural-language-processing, audio, tabular, reinforcement-learning (could be more than one)\n "
TASK_PROMPT = "- tasks: feature-extraction, text-to-image, image-to-text, text-to-video, visual-question-answering, document-question-answering, graph-machine-learning, depth-estimation, image-classification, object-detection, image-segmentation, image-to-image, unconditional-image-generation, video-classification, zero-shot-image-classification, text-classification, token-classification, table-question-answering, question-answering, zero-shot-classification, translation, summarization, conversational, text-generation, text2text-generation, fill-mask, sentence-similarity, text-to-speech, automatic-speech-recognition, audio-to-audio, audio-classification, voice-activity-detection, tabular-classification, tabular-regression, reinforcement-learning, robotics\n "
LANG_PROMPT = "- language: return supported languages for this model\n "