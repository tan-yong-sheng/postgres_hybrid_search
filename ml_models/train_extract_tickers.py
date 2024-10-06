from pathlib import Path

import spacy

from db_connection import db_context
from db_models import StockSymbolOrm
from schemas import ExtractTicker


def label_stock_code(label: str, text: str):
    text = text.lower()
    return [
        {
            "label": label,
            "pattern": [{"TEXT": "("}, {"LOWER": text}, {"TEXT": ")"}],
        },
        {"label": label, "pattern": [{"LOWER": text}]},
        {"label": label, "pattern": [{"LOWER": f"{text}.kl"}]},
        {"label": label, "pattern": [{"LOWER": f"{text}.kls"}]},
        {"label": label, "pattern": [{"LOWER": f"{text}.klse"}]},
        {"label": label, "pattern": [{"LOWER": f"{text}.my"}]},
        {"label": label, "pattern": [{"LOWER": "kl"}, {"TEXT": ":"}, {"LOWER": text}]},
        {
            "label": label,
            "pattern": [{"LOWER": "kls:"}, {"TEXT": ":"}, {"LOWER": text}],
        },
        {
            "label": label,
            "pattern": [{"LOWER": "klse:"}, {"TEXT": ":"}, {"LOWER": text}],
        },
    ]


def label_stock_symbol(label: str, text: str):
    text = text.lower()
    return [
        {
            "label": label,
            "pattern": [{"TEXT": "("}, {"LOWER": text}, {"TEXT": ")"}],
        },
        {
            "label": label,
            "pattern": [{"LOWER": f"{text}.kl"}],
        },
        {
            "label": label,
            "pattern": [{"LOWER": f"{text}.kls"}],
        },
        {
            "label": label,
            "pattern": [{"LOWER": f"{text}.my"}],
        },
        {
            "label": label,
            "pattern": [{"LOWER": "kl"}, {"TEXT": ":"}, {"LOWER": text}],
        },
        {
            "label": label,
            "pattern": [{"LOWER": "kls"}, {"TEXT": ":"}, {"LOWER": text}],
        },
        {
            "label": label,
            "pattern": [{"LOWER": "klse"}, {"TEXT": ":"}, {"LOWER": text}],
        },
    ]


def label_company_name(label: str, text: str):
    text = text.lower()
    words = text.split()
    patterns = []
    if len(words) > 1:
        # Original pattern
        pattern1 = {"label": label, "pattern": []}
        for idx, word in enumerate(words):
            pattern1["pattern"].append({"LOWER": word})
        patterns.append(pattern1)

        # Pattern with last word replaced by "berhad"
        pattern2 = {"label": label, "pattern": []}
        for idx, word in enumerate(words):
            if idx == len(words) - 1 and word == "bhd":
                pattern2["pattern"].append({"LOWER": "berhad"})
            else:
                pattern2["pattern"].append({"LOWER": word})
        patterns.append(pattern2)

        # Pattern with last word replaced by "bhd"
        pattern3 = {"label": label, "pattern": []}
        for idx, word in enumerate(words):
            if idx == len(words) - 1 and word == "berhad":
                pattern3["pattern"].append({"LOWER": "bhd"})
            else:
                pattern3["pattern"].append({"LOWER": word})
        patterns.append(pattern3)
    return patterns


with db_context() as db_session:
    stock_symbols = db_session.query(StockSymbolOrm).all()
    stock_symbols = [
        ExtractTicker(**stock_symbol.__dict__) for stock_symbol in stock_symbols
    ]

    # Initialize the spaCy pipeline with the entity ruler component
    nlp = spacy.blank("en")
    ruler = nlp.add_pipe("entity_ruler")
    patterns = []

    # Add stock_code and stock_symbol patterns with case variations
    for item in stock_symbols:
        patterns += label_stock_code("STOCK_CODE", item.stock_code)
        patterns += label_stock_symbol("STOCK_SYMBOL", item.stock_symbol)
        patterns += label_company_name("COMPANY_NAME", item.company_name)

    # Add all patterns to the entity ruler
    ruler.add_patterns(patterns)

    # Save the model
    nlp.to_disk(path=Path(__file__).parent / "extract_tickers_model")
