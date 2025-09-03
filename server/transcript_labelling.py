from youtube_transcript_api import YouTubeTranscriptApi
import json 
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch
import os 
from dotenv import load_dotenv
from huggingface_hub import login 

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

        segments.append({
            'text':segment_text,
            'start':segment_start, 
            'label': predicted_class #default label
        })

    return segments

def compute_intervals(data, interval_threshold = 5): 
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
            'end_time' : data[i+1]['start']
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
                i+=1 
            else: 
                i = j 
                break

    return intervals_merged
