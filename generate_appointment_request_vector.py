'''
This script will take each request phrases in the phrases_appointment_request_vectory.json and will generate the equivalent 
the equivalent of vector value.  So if there are new phrases to add, you can just simply add
them in the phrases json file, run this script and it will save everything in the enriched_data.json
'''
from transformers import BertTokenizer, BertModel, AutoTokenizer, AutoModel
import torch
import json
# Initialize the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

def get_embedding(text):
    """
    Generate vector embeddings for the given text.
    """
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(1).detach().numpy()
    return embeddings.tolist()[0]

def enrich_data_with_vectors(filename):
    """
    Load requests from the given JSON file, compute embeddings, and save enriched data.
    """
    with open(f'./assets/{filename}', 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    for entry in data:
        request_text = entry['request']
        vector = get_embedding(request_text)
        entry['vector'] = vector
    
    # Save enriched data to a new file
    enriched_filename = './assets/enriched_data.json'
    with open(enriched_filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    
    print(f"Enriched data saved to {enriched_filename}")

if __name__ == "__main__":
    filename = 'phrases_appointment_request.json'
    enrich_data_with_vectors(filename)
