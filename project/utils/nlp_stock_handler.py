import spacy
from spacy.tokens import Span


# Function to retrieve the stock exchange (or other metadata) for the matched ticker
def get_stock_exchange(span):
    span_text = span.text.upper()
    if span.label_ == "STOCK_SYMBOL" or span.label_ == "STOCK_CODE":
        span_text = span_text.replace("(", "").replace(")", "")
        if span_text.endswith((".KL", ".KLS", ".MY")) or span_text.startswith(
            ("KLSE:", "KLS:", "KL:")
        ):
            return "Bursa"
    elif span.label_ == "STOCK_CODE":
        span_text = span_text.replace("(", "").replace(")", "")

    elif span.label_ == "COMPANY_NAME":
        if span_text.endswith(("BERHAD", "BHD")):
            return "Bursa"


def get_entity_name(span):
    import re

    span_text = span.text.upper()
    if span.label_ in ("STOCK_SYMBOL", "STOCK_CODE"):
        span_text = span_text.replace("(", "").replace(")", "")
        span_text = re.sub(r"\.(KL|KLS|MY)$", "", span_text)
        span_text = re.sub(r"^(KLSE|KLS|KL):", "", span_text)
        return span_text

    elif span.label_ == "COMPANY_NAME":
        span_text = re.sub(r"(CORP|CORPORATION)?\s(BERHAD|BHD)$", "", span_text)
        return span_text.strip()


# Register the Span extension "exchange" with the getter function
Span.set_extension("exchange", getter=get_stock_exchange)
Span.set_extension("entity_name", getter=get_entity_name)


# Load the pre-trained spaCy model (you can use 'en_core_web_sm' or a larger model)
nlp = spacy.load("project/ml_models/extract_tickers_model")


def extract_financial_entities(text: str):
    # recognize company names, stock symbols, and stock codes in the text
    doc = nlp(text)
    financial_entities = []
    for ent in doc.ents:
        financial_entities.append(
            {
                "exchange": ent._.exchange,
                "entity_name": ent._.entity_name,
                "entity_type": ent.label_,
            }
        )
    return financial_entities
