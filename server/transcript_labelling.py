from youtube_transcript_api import YouTubeTranscriptApi
import json 
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch
import os 

ytt_api =YouTubeTranscriptApi()

# Load the saved model and tokenizer
model_path = os.path.join(os.path.dirname(__file__), '../model/ad-classifier')#'./ad-classifier'  # e.g. './distilbert_model'
print(model_path)
tokenizer = DistilBertTokenizer.from_pretrained(model_path)
model = DistilBertForSequenceClassification.from_pretrained(model_path)

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

