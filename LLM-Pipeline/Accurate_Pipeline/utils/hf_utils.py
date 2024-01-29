import huggingface_hub

def load_card(model_name: str) -> str:

    try:
        card = huggingface_hub.ModelCard.load(model_name)
    except huggingface_hub.utils._errors.RepositoryNotFoundError:
        print(f"{model_name} repo not found\n")
        #card.data = tags
        #card.text card
        #cald.content tags+cards
    card = "#tags\n\n" + card.content
    card = card.replace('"', "'")
    return (card)
    
def get_domain_and_task(model_name: str) -> (list,list):
    model_info = huggingface_hub.hf_api.model_info(model_name)
    tags = model_info.tags
    domain = []
    model_task = []

    tasks = {
    "multimodal":["feature-extraction", "text-to-image", "image-to-text", "text-to-video", "visual-question-answering", "document-question-answering", "graph-machine-learning"],
    "computer-vision":["depth-estimation", "image-classification", "object-detection", "image-segmentation", "image-to-image", "unconditional-image-generation", "video-classification", "zero-shot-image-classification"],
    "natural-language-processing":["text-classification", "token-classification", "table-question-answering", "question-answering", "zero-shot-classification", "translation", "summarization", "conversational", "text-generation", "text2text-generation", "fill-mask", "sentence-similarity"], 
    "audio":["text-to-speech", "automatic-speech-recognition", "audio-to-audio", "audio-classification", "voice-activity-detection"],
    "tabular":["tabular-classification", "tabular-regression"],
    "reinforcement-learning":["reinforcement-learning", "robotics"]
    }

    for tag in tags:
        for key, value in tasks.items():
            if tag in value:
                domain.append(key)
                model_task.append(tag)

    return (domain, model_task)

def get_frameworks(model_name: str) -> list:
    frameworks = ["pytorch", "tf", "jax"]
    tags = huggingface_hub.hf_api.model_info(model_name).tags

    return list(set(tags) & set(frameworks))

def get_libraries(model_name: str) -> list:
    libraries = ["transformers", "tensorboard", "diffusers", "stable-baselines3", "safetensors", "peft", "onnx", 
                  "ml-agents", "sentence-transformers", "timm", "sample-factory", "keras", "adapter-transformers", "flair", "spacy", "espnet", 
                  "transformers.js", "fastai", "coreml", "rust", "nemo","joblib","scikit-learn","fasttext","speechbrain","paddlepaddle","openclip",
                  "bertopic", "fairseq", "openvino", "graphcore", "stanza", "tf-lite", "asteroid", "paddlenlp", "allennlp", "spanmarker", "habana", 
                  "pythae", "pyannote.audio"]
    tags = huggingface_hub.hf_api.model_info(model_name).tags

    return list(set(tags) & set(libraries))

