from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")

# Create NER pipeline
nlp = pipeline("ner", model=model, tokenizer=tokenizer, grouped_entities=True)

def get_orgs(text): 

    ner_results = nlp(text)
    orgs = list(set([ent['word'] for ent in ner_results if ent['entity_group'] == 'ORG' and ent['score'] > 0.8]))

    return orgs