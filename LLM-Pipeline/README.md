# Enhancement of PeaTMOSS via Metadata Extraction


## About

This repository contains the source code that we created in assistance for our metadata extraction pipeline ($5)

## Table of Contents
- [Cheap Pipeline](/LLM-Pipeline/Cheap_Pipeline/)
- [Accureate Pipeline](/LLM-Pipeline/Accurate_Pipeline/)

## Metadata Table

| Paper | Newly Introduced Metadata of Interest |
|-------|---------------------------------------|
| Schelter et al., 2017 \[82\] | Model name, model version, framework, tags, dataset name, dataset version, dataset statistic, data transform, input/output format, evaluation, training time, environment, hyperparameters, prediction metadata |
| Tsay et al., 2020 \[89\] | Reference, domain, has README, uses Python, popularity |
| Li et al., 2022 \[64\] | Model architecture, task, hardware |
| Tsay et al., 2022 \[90\] | Description, code, training job, training output, provenance |
| PeaTMOSS | Carbon emitted, model size, license, base model, limitation and biases, demonstration, grant/sponsorship, language (NLP) |


> Detailed mapping from our extracted metadata to the metadata mentioned in prior papers. The extracted output is avaiable in our database, and has a json format in [extracted metadata](/LLM-Pipeline/final_result.json)

| Metadata | Location in PeaTMOSS |
|----------|----------------------|
| Model name and version | `model_id` |
| Framework | `framework` |
| Tags | `tags` |
| Dataset name and version | `dataset_id` |
| Dataset statistic | `N/A` |
| Data transform | `demo` |
| Input/output format | `input_format`, `output_format` |
| Evaluation | `evaluation_link`, `evaluation_metric` |
| Training time | `hardware/hours_used` |
| Environment | `demo` |
| Hyperparameters | `hyper_parameters` |
| Prediction metadata | `demo` |
| Reference | `paper_id` |
| Domain | `domain_id` |
| Has README | `tag` |
| Uses Python | `N/A` |
| Popularity | `downloads`, `likes` |
| Model architecture | `architecture` |
| Task | `model_task` |
| Hardware | `hardware` |
| Description | `tags` |
| Code | `model_github_repo` |
| Training job | `demo` |
| Training output | `output_format` |
| Provenance | `paper_id`, `dataset_id` |
| Carbon emitted | `carbon_emitted` |
| Model size | `model_size` |
| License | `license` |
| Base model | `base_model` |
| Limitation and biases | `limitation_and_bias` |
| Demonstration | `demo` |
| Grant/sponsorship | `grant_id` |
| Language (NLP) | `language_id` |
