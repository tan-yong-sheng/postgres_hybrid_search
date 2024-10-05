import spacy

# Load the pre-trained spaCy model (you can use 'en_core_web_sm' or a larger model)
nlp = spacy.load("ml_models/train_extract_tickers.spacy")

# Test the NER on an example text
doc = nlp("John works at genting malaysia and met Elon Musk.")

# Print the recognized PERSON and ORG entities
for ent in doc.ents:
    print(ent.text, ent.label_)
