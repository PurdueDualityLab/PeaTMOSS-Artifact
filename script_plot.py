
import matplotlib.pyplot as plt
import sqlite3
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates
from collections import defaultdict
import re
import json
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Function Definitions
def queryit(cursor, query): 
    cursor.execute(query)
    return cursor.fetchall()

def calculate_frequency(models_per_task):
    frequency_data = {}
    for task, timestamps in models_per_task.items():
        frequency = {}
        for timestamp in timestamps:
            year_month = timestamp[:7]  # Extract Year-Month
            frequency[year_month] = frequency.get(year_month, 0) + 1
        frequency_data[task] = frequency
    return frequency_data

def parse_single_file(url):
    response = requests.get(url)
    return response.content.decode("utf-8")

def extract_params(returned): 
    match = re.search(r'">(.*?) params<', returned)
    return match.group(1) if match else None

def replace_tag(row_dict, tag_to_domain): 
    for repo_url in row_dict:
        row_dict[repo_url]['domain.name'] = None
        for domain in tag_to_domain: 
            if row_dict[repo_url]['tag.name'] in tag_to_domain[domain]: 
                row_dict[repo_url]['domain.name'] = domain

def mil_bil(x):
    try:  
        if 'M' in x: 
            return 1000000 * float(re.sub('(M)', '', x))
        elif 'B' in x: 
            return 1000000000 * float(re.sub('(B)', '', x))
        else: 
            return 0
    except ValueError: 
        return 0 

def remove_outliers(data):
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return [x for x in data if lower_bound <= x <= upper_bound]

def to_9month_interval(date):
    year, month = date.year, date.month
    if month <= 9: 
        return f"{year}-01 to {year}-09"
    else: 
        return f"{year}-10 to {year + 1}-06"

def main():
    # Constants and global variables
    hf_domains  = {
        'Multimodal': ['feature-extraction', 'text-to-image', 'image-to-text', 'text-to-video', 'visual-question-answering', 'graph-machine-learning'],
        'Computer Vision': ['depth-estimation', 'image-classification', 'object-detection', 'image-segmentation', 'image-to-image', 'unconditional-image-generation', 'video-classification', 'zero-shot-image-classification'],
        'NLP': ['text-classification', 'token-classification', 'table-question-answering', 'question-answering', 'zero-shot-classification', 'translation', 'summarization', 'conversational', 'text-generation', 'text2text-generation', 'fill-mask', 'sentence-similarity', 'table-to-text', 'multiple-choice', 'text-retrieval'],
        'Audio': ['text-to-speech', 'text-to-audio', 'automatic-speech-recognition', 'audio-to-audio', 'audio-classification', 'voice-activity-detection'],
        'Other': ['reinforcement-learning', 'robotics', 'tabular-classification', 'tabular-regression', 'tabular-to-text', 'time-series-forecasting']
    }

    pytorch_domains = {
        'NLP': ['nlp'],
        'Multimodal': ['scriptable', 'generative', 'video'],
        'Computer Vision': ['object_detection', 'segmentation', 'vision', 'optical_flow'],
        'Audio': ['audio'],
        'Other': ['researchers', 'cuda-optional', 'cuda', 'quantization']
    }

    tag_to_domain = {'Multimodal': ['feature-extraction', 'text-to-image', 'image-to-text', 'text-to-video', 'visual-question-answering', 'graph-machine-learning'], 'Computer Vision': ['depth-estimation', 'image-classification', 'object-detection', 'image-segmentation', 'image-to-image', 'unconditional-image-generation', 'video-classification', 'zero-shot-image-classification'], 'NLP': ['text-classification', 'token-classification', 'table-question-answering', 'question-answering', 'zero-shot-classification', 'translation', 'summarization', 'conversational', 'text-generation', 'text2text-generation', 'fill-mask', 'sentence-similarity', 'table-to-text', 'multiple-choice', 'text-retrieval'], 'Audio': ['text-to-speech', 'text-to-audio', 'automatic-speech-recognition', 'audio-to-audio', 'audio-classification', 'voice-activity-detection'], 'Reinforcement Learning': ['reinforcement-learning', 'robotics'], 'Other': ['tabular-classification', 'tabular-regression', 'tabular-to-text', 'time-series-forecasting']}


    # Load JSON data
    json_file = {}
    with open('./final_result.json', 'r') as file: 
        json_file = json.load(file)

    hf_task_names = [y for x in hf_domains.values() for y in x]

    # Database Connection
    conn = sqlite3.connect('./PeaTMOSS.db')
    cursor = conn.cursor()


    hub_id = 1
    models_per_task = defaultdict(list)

    query = f'''
        SELECT tag.name,hf_commit.created_at
        FROM model
        INNER JOIN model_to_tag ON model.id = model_to_tag.model_id
        INNER JOIN tag ON model_to_tag.tag_id = tag.id
        INNER JOIN hf_commit ON hf_commit.model_id = model.id
        WHERE model.model_hub_id = {hub_id}
    '''


    # Execute query
    rows = queryit(cursor, query)
    for row in rows: 
        tag_name, created_at = row
        if tag_name in hf_task_names:
            models_per_task[tag_name].append(created_at)

            
    # Calculate frequency for each task
    frequency_data_per_task = calculate_frequency(models_per_task)

    data_dict = {} 
    data = hf_domains
    for problem in data: 
        tasks = data[problem]
        # initalize an empty dictionary and add the dates as columns and freqeucny as the values
        data_dict[problem] = {}
        for task in tasks: 
            if task in frequency_data_per_task:
                dates = [x for x in list(frequency_data_per_task[task].keys()) if x not in ['2023-06', '2023-07', '2023-08']]

                for date in dates: 
                    if date not in data_dict[problem]:
                        data_dict[problem][date] = frequency_data_per_task[task][date]
                    else: 
                        data_dict[problem][date] += frequency_data_per_task[task][date]

    data_dict = {key: dict(sorted(value.items())) for key, value in data_dict.items()}


    sorted_data_dict = {}
    for key, values in data_dict.items():
        sorted_values = sorted(values.items(), key=lambda x: datetime.strptime(x[0], '%Y-%m'))
        sorted_data_dict[key] = {datetime.strptime(k, '%Y-%m'): v for k, v in sorted_values}

    fig, ax = plt.subplots(figsize=(20, 15))

    # Define colors for the lines (same order as the categories)
    colors = ['blue', 'green', 'red', 'purple', 'black']  # Adjust as per your categories

    for (key, values), color in zip(sorted_data_dict.items(), colors):
        if values:
            dates = list(values.keys())
            freqs = list(values.values())

            # Plot line
            ax.plot(dates, freqs, marker='o', linewidth=1, alpha=1, label=key, color=color, markersize=10)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=9))  # Adjust interval as needed
    plt.xticks(rotation=30, fontsize=38)
    plt.yticks(fontsize=35)

    # Add legend and labels
    plt.legend(fontsize=35)
    plt.xlabel("Year", fontsize=50)
    plt.ylabel("Frequency", fontsize=50)
    plt.grid(linestyle='--', linewidth=0.5, color='gray')
    plt.tight_layout()
    

    plt.savefig('./saves/first_line.png')


    hub_id = 1
    query = '''
        SELECT 
            tag.name AS TagName,
            COUNT(DISTINCT model_to_reuse_repository.reuse_repository_id) AS number
        FROM 
            model
        INNER JOIN model_to_tag ON model.id = model_to_tag.model_id
        INNER JOIN tag ON model_to_tag.tag_id = tag.id
        INNER JOIN model_to_reuse_repository ON model.id = model_to_reuse_repository.model_id
        WHERE 
            model.model_hub_id = 1
        GROUP BY 
            tag.name;
    '''
    rows_hub1 = queryit(cursor, query)

    # Assuming hf_domains is predefined as in your original code
    domain_counts_hub1 = {key: 0 for key in hf_domains.keys()} 
    for name, count in rows_hub1: 
        for domain in hf_domains: 
            if name in hf_domains[domain]: 
                domain_counts_hub1[domain] += count
    # Replcae counts with percentage values of count / total github repositories returned
    total1 = sum(domain_counts_hub1.values())
    values1 = domain_counts_hub1.copy()
    domain_counts_hub1 = {key: 100* (value / total1) for key, value in domain_counts_hub1.items()}
    rows1_hub1 = dict(sorted(domain_counts_hub1.items(), key=lambda item: item[1], reverse=True))


    hub_id = 2
    query = '''
        SELECT 
            tag.name AS TagName,
            COUNT(DISTINCT model_to_reuse_repository.reuse_repository_id) AS number
        FROM 
            model
        INNER JOIN model_to_tag ON model.id = model_to_tag.model_id
        INNER JOIN tag ON model_to_tag.tag_id = tag.id
        INNER JOIN model_to_reuse_repository ON model.id = model_to_reuse_repository.model_id
        WHERE 
            model.model_hub_id = 2
        GROUP BY 
            tag.name;
    '''
    rows_hub2 = queryit(cursor, query)

    domain_counts_hub2 = {key: 0 for key in hf_domains.keys()} 
    for name, count in rows_hub2: 
        for domain in pytorch_domains: 
            if name in pytorch_domains[domain]: 
                domain_counts_hub2[domain] += count
    total2 = sum(domain_counts_hub2.values())
    values2 = domain_counts_hub2.copy()
    domain_counts_hub2 = {key: 100 * (value / total2) for key, value in domain_counts_hub2.items()}
    rows1_hub2 = dict(sorted(domain_counts_hub2.items(), key=lambda item: item[1], reverse=True))


    tags = list(rows1_hub1.keys())

    # Get frequencies for both hub_ids
    freq_hub1 = [rows1_hub1.get(tag, 0) for tag in tags]
    freq_hub2 = [rows1_hub2.get(tag, 0) for tag in tags]

    # Bar plot settings
    bar_width = 0.35
    index = np.arange(len(tags))

    plt.figure(figsize=(15, 13))

    plt.bar(index, freq_hub1, bar_width, alpha=1, label='Hugging Face Hub')
    plt.bar(index + bar_width, freq_hub2, bar_width, alpha=1, label='PyTorch Hub')
    for i in index: 
        text1 = total1 * (freq_hub1[i] / 100)
        text2 = total2 * (freq_hub2[i] / 100)

    # If text1 is in the thousands, I want to append a K to the end of it 
    if text1 > 1000: 
        text1 = str(round((text1 / 1000), 1)) + 'K'
    else: 
        text1 = str(round(text1)) 
    if text2 > 1000:
        text2 = str(round((text2 / 1000), 1)) + 'K'
    else:
        text2 = str(round(text2)) 


    plt.text(i, freq_hub1[i] + 4, text1 , ha = 'center', fontsize = 38, rotation=90)
    plt.text(i + bar_width, freq_hub2[i] + 4, text2, ha = 'center', fontsize = 38, rotation=90)

    plt.xlabel('Domain', fontsize=47)
    plt.ylabel('Frequency (%)', fontsize=47)
    plt.xticks(index + bar_width / 2, tags, rotation=20, fontsize=28, ha='right')
    plt.yticks(fontsize=34)
    plt.xticks(fontsize=34)

    # plt.yscale('log')
    plt.legend(fontsize=39)
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig('./saves/hf_py_downstream.png')


    hub_id = 1
    query = '''
        SELECT 
            model.id, tag.name
        FROM 
            model
        INNER JOIN model_to_tag ON model.id = model_to_tag.model_id
        INNER JOIN tag ON model_to_tag.tag_id = tag.id
        WHERE 
            model.model_hub_id = 1
    '''

    # Make a dictionary mapping to the number of models per domain using hf_domains
    rows = queryit(cursor, query)
    domain_counts = {key: 0 for key in hf_domains.keys()}
    for model_id, name in rows: 
        for domain in hf_domains: 
            if name in hf_domains[domain]: 
                domain_counts[domain] += 1

    # convert this into percentages
    total1 = sum(domain_counts.values())
    values1 = domain_counts.copy()
    domain_counts1 = {key: 100 * (value / total1) for key, value in domain_counts.items()}

    # Sort the dictionary by values
    rows1 = dict(sorted(domain_counts1.items(), key=lambda item: item[1], reverse=True))


    hub_id = 2
    query = '''
        SELECT 
            model.id, tag.name
        FROM 
            model
        INNER JOIN model_to_tag ON model.id = model_to_tag.model_id
        INNER JOIN tag ON model_to_tag.tag_id = tag.id
        WHERE 
            model.model_hub_id = 2
    '''

    # Make a dictionary mapping to the number of models per domain using hf_domains
    rows = queryit(cursor, query)
    domain_counts = {key: 0 for key in hf_domains.keys()}
    for model_id, name in rows: 
        for domain in pytorch_domains: 
            if name in pytorch_domains[domain]: 
                domain_counts[domain] += 1

    # convert this into percentages
    total2 = sum(domain_counts.values())
    values2 = domain_counts.copy()
    domain_counts2 = {key: 100 * (value / total2) for key, value in domain_counts.items()}

    # Sort the dictionary by values
    rows2 = dict(sorted(domain_counts2.items(), key=lambda item: item[1], reverse=True))


    tags = list(rows1.keys())

    # Get frequencies for both hub_ids
    freq_hub1 = [rows1.get(tag, 0) for tag in tags]
    freq_hub2 = [rows2.get(tag, 0) for tag in tags]

    # Bar plot settings
    bar_width = 0.35
    index = np.arange(len(tags))

    plt.figure(figsize=(15, 13))

    plt.bar(index, freq_hub1, bar_width, alpha=1, label='Hugging Face Hub')
    plt.bar(index + bar_width, freq_hub2, bar_width, alpha=1, label='PyTorch Hub')
    for i in index: 
        text1 = total1 * (freq_hub1[i] / 100)
        text2 = total2 * (freq_hub2[i] / 100)

    # If text1 is in the thousands, I want to append a K to the end of it 
    if text1 > 1000: 
        text1 = str(round((text1 / 1000))) + 'K'
    else: 
        text1 = str(round(text1)) 
    if text2 > 1000:
        text2 = str(round((text2 / 1000))) + 'K'
    else:
        text2 = str(round(text2)) 

    plt.text(i, freq_hub1[i] + 4, text1, ha = 'center', fontsize = 38, rotation=90)
    plt.text(i + bar_width, freq_hub2[i] + 4, text2, ha = 'center', fontsize = 38, rotation=90)

    plt.xlabel('Domain', fontsize=47)
    plt.ylabel('Frequency (%)', fontsize=47)
    plt.xticks(index + bar_width / 2, tags, rotation=20, fontsize=28, ha='right')
    plt.yticks(fontsize=34)
    plt.xticks(fontsize=34)

    # plt.yscale('log')
    plt.legend(fontsize=39)
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig('./saves/hf_py_model_counts.png')

    sample = [] 

    for repo_url in json_file:
      if not  type(json_file[repo_url]) == str: 
        for meta in json_file[repo_url]: 
          if meta not in sample: 
            sample.append(meta)

    noise = [ 
      'model_name',
    'model_type',
    'model_card',
    'duplicated_from',
    'library_tag',
    'tags',
    'library_name',
    'original',
    'pipeline_tag',
    'pipeline',
    'model_usage',
    'metrics',
    'widget',
    'inference',
    'framework_versions',
    'description'
    ]



    # Remove all noise from samples 
    for i in range(len(sample)): 
      if sample[i] in noise: 
        sample[i] = None

    sample = [x for x in sample if x is not None]

    popular_meta = sample 


    TOTAL = len(json_file)


    cat_meta_count = {key: 0 for key in popular_meta} 


    for model in json_file: 
      for meta in json_file[model]: 
        if meta in popular_meta:
          if json_file[model][meta]:
            cat_meta_count[meta] += 1

    sorted_cat_meta_count = {k: round((v/TOTAL) * 100, 2) for k, v in sorted(cat_meta_count.items(), key=lambda item: item[1], reverse=True)} 


    tags, freq = [x for x in sorted_cat_meta_count], [sorted_cat_meta_count[x] for x in sorted_cat_meta_count]

    # Create a bar chart
    plt.figure(figsize=(19, 17))  # Adjust the figure size as needed
    plt.bar(tags, freq, color='blue', alpha=0.9)
    plt.bar(tags, [100-x for x in freq], color='white', alpha=0.8, bottom=freq)
    for i in range(len(tags)): 
      text1 = (freq[i]/100) * TOTAL
      if text1 > 1000: 
        text1 = str(round((text1 / 1000), 1)) + 'K'
      else: 
        text1 = str(round(text1))
      plt.text(i, freq[i] + 4, text1, ha = 'center', fontsize = 38, rotation=90)
    plt.xlabel('Metadata Tags', fontsize=50)
    plt.ylabel('Proportion of Availabile Data (%)', fontsize=50)
    plt.yticks(fontsize=34)
    plt.xticks(rotation = 40, fontsize=39, ha='right')
    plt.tight_layout()  # Adjust layout to fit the labels
    plt.savefig('./saves/meta.png') 

    param_count = {url: {} for url in json_file}


    mapping = {'natural-language-processing': "NLP", "multimodal": "Multimodal", "audio": "Audio", "computer-vision": "Computer Vision", "reinforcement-learning": "Reinforcement Learning", "graph-machine-learning": "Multimodal", "robotics": "Reinforcement Learning", "tabular": "Other", "time-series": "Other"}


    for model in json_file:
      if not type(json_file[model]) == str:
        if json_file[model]["domain"]:
          if type(json_file[model]["domain"]) == list: 
            adomain = json_file[model]["domain"][0]
          else:
            adomain = json_file[model]["domain"]
          if "," in adomain: 
            adomain = adomain.split(",")[0]
          
          param_count[model]["domain"] = mapping[adomain] 
          param_count[model]["params"] = ""
        else: 
          param_count[model]["domain"] = "Other"
          param_count[model]["params"] = ""

        for meta in json_file[model]: 
          if meta == "parameter_count": 
            param_count[model]['params'] = json_file[model][meta]

    store = param_count.copy()


    for model in param_count: 
      if not param_count[model]: 
        del store[model]

    param_count = store


    urls = [f'"https://huggingface.co/{x}"' for x in param_count.keys()]

    query = f'''
          SELECT model.repo_url, hf_commit.created_at
          FROM model
          INNER JOIN hf_commit ON hf_commit.model_id = model.id
          WHERE model.repo_url IN ({','.join(urls)})
      '''
    rows = queryit(cursor, query)



    for row in rows: 
      url = row[0].replace('https://huggingface.co/', '')
      param_count[url]['date'] = row[1]


    data_list = [[model_name] + list(details.values()) for model_name, details in param_count.items()]

    df = pd.DataFrame(data_list, columns=['name', 'domain', 'params', 'date'])

    df = df[df.params != '']

    df = df.dropna()

    def mil_bil(x):
      try:  
        if 'M' in x: 
          return 1000000 * float(re.sub('(M)', '', x))
        elif 'B' in x: 
          return 1000000000 * float(re.sub('(B)', '', x)) 
        else: 
          return 0
      except ValueError: 
        return 0 

    df.params = df.params.apply(lambda x: mil_bil(x))


    df = df[df.params != 0]

    df.date = pd.to_datetime(df.date)


    df.sort_values(by=['date'], inplace=True)


    df.dropna(inplace=True)


    domain_params_dict = {domain: list(group['params']) for domain, group in df.groupby('domain')}
    domain_date_dict = {domain: list(group['date']) for domain, group in df.groupby('domain')}


    def remove_outliers(data):
        # Calculate Q1, Q3 and IQR
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1

        # Define bounds for outliers
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Filter out outliers and return the result
        return [x for x in data if lower_bound <= x <= upper_bound]

    pd.plotting.register_matplotlib_converters()

    def to_9month_interval(date):
        year, month = date.year, date.month
        if month <= 9:  # From January to September
            return f"{year}-01 to {year}-09"
        else:  # From October to June of the next year
            return f"{year}-10 to {year + 1}-06"
    df['9_month_interval'] = df['date'].apply(to_9month_interval)

    # Convert 'date' to datetime if it's not already
    df['date'] = pd.to_datetime(df['date'])

    # Group data by 6-month intervals
    # Note: 'QS' stands for quarter start frequency, which aligns with 6-month intervals in this context
    grouped_median = df.groupby(['domain', pd.Grouper(key='date', freq='6M')])['params'].median().reset_index()

    # Formatting the date for plotting
    grouped_median['formatted_date'] = grouped_median['date'].dt.strftime('%Y-%m')
    all_dates = grouped_median['formatted_date'].unique()
    # Get unique domains
    domains = df['domain'].unique()

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(19, 15))

    # Colors for different domains (adjust as per the number of domains)
    colors = ['blue', 'green', 'red', 'purple']

    # # Plotting the median values for each domain in 6-month intervals
    for domain, color in zip(domains, colors):
        domain_data = grouped_median[grouped_median['domain'] == domain]
        ax.plot(domain_data['formatted_date'].astype(str), domain_data['params']/1000000000, marker='o', markersize=15, color=color, label=f'{domain} (median)', linewidth=4)



    # Format x-axis for better date representation
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6)) 
    ax.set_xticks(all_dates)
    ax.tick_params(axis='x', rotation=35)
    plt.xticks(fontsize=35)
    plt.yticks(fontsize=35)
    ax.legend(fontsize=39)
    ax.set_xlabel('Year', fontsize = 52)
    ax.set_ylabel('Median Parameter Count (Billion)', fontsize = 52)
    ax.grid(True)

    # Show plot
    plt.tight_layout()
    plt.savefig('./saves/median.png')



# Executing the main function
if __name__ == '__main__':
    main()
