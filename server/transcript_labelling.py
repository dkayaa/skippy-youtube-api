from youtube_transcript_api import YouTubeTranscriptApi
import json 
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch
import os 
from dotenv import load_dotenv
from huggingface_hub import login 
from org_extractor import get_orgs 

ytt_api =YouTubeTranscriptApi()
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Load model and tokenizer from Hugging Face
model_name = os.getenv("HUGGINGFACE_MODEL")
tokenizer = DistilBertTokenizer.from_pretrained(model_name)
model = DistilBertForSequenceClassification.from_pretrained(model_name)

# Put model in evaluation mode
model.eval()

def get_labelled_tscript(video_id):
    try:
        fetched_transcript = ytt_api.fetch(video_id)
    except Exception as e: 
        print(e)
    
    if len(fetched_transcript) == 0 : 
        return [] 
    
    window_size = 10
    stride =5
    segments = []

    
    for i in range(0, len(fetched_transcript) - window_size, stride):
        segment_text = " ".join([snippet.text for snippet in fetched_transcript[i:i+window_size]])
        segment_start = fetched_transcript[i].start 

        inputs = tokenizer(segment_text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)

        # Get prediction
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()
        
        # org ner extraction 
        orgs = get_orgs(segment_text)

        segments.append({
            'text':segment_text,
            'start':segment_start, 
            'label': predicted_class, #default label
            'orgs' : orgs
        })

    return segments

def compute_intervals(data, interval_threshold = 5, min_duration = 45): 
    """
    input: list of dicts with keys 'text', 'start', 'label' 
    
    output: list of dicts with keys 'start_time', 'end_time' 
    """

    # sort data 
    data.sort(key=lambda x: x['start'])

    # convert to new interval representation
    intervals = [] 

    for i in range(0, len(data) - 1): 
        if data[i]['label'] == 0: 
            continue 
        intervals.append({
            'start_time': data[i]['start'], 
            'end_time' : data[i+1]['start'],
            'orgs': data[i].get('orgs', [])
        })

    # merge intervals 
    intervals_merged = [] 

    i = 0 
    j = 0 
    while i < len(intervals): 
        intervals_merged.append(intervals[i].copy())
        for j in range(i, len(intervals)): 
            if intervals[j]['start_time'] - intervals_merged[-1]['end_time'] <= interval_threshold: 
                intervals_merged[-1]['end_time'] = intervals[j]['end_time']
                intervals_merged[-1]['orgs'] = list(set(intervals_merged[-1].get('orgs', []) + intervals[j].get('orgs', [])))
                i+=1 
            else: 
                i = j 
                break

    # Post Process Intervals 
    # 1. Remove Short intervals 
    intervals_merged = [x for x in intervals_merged if x['end_time'] - x['start_time'] > min_duration]
    
    # 2. add Unknown Tag 
    for interval in intervals_merged: 
        if len(interval['orgs']) == 0: 
            interval['orgs'] = ['UNKNOWN']
    
    print(intervals_merged)
    
    return intervals_merged
