import spacy

# Load the pre-trained spaCy model (you can use 'en_core_web_sm' or a larger model)
nlp = spacy.load("ml_models/extract_tickers_model")


def extract_financial_entities(text: str):
    doc = nlp.make_doc(text)
    financial_entities = []
    for ent in doc.ents:
        print(ent.text, ent.label_)
        financial_entities.append({"entity_name": ent.text, "entity_type": ent.label_})
    return financial_entities
