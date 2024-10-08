from pathlib import Path

import spacy

from db_connection import db_context
from db_models import StockSymbolOrm
from schemas import ExtractTicker


def label_stock_code(label: str, text: str):
    # Assuming stock code is 4715
    text = text.lower()
    return [
        ## match (4715)
        {
            "label": label,
            "pattern": [
                {"TEXT": "(", "OP": "*"},
                {"LOWER": text},
                {"TEXT": ")", "OP": "*"},
            ],
        },
        ## match (4715.KL) or (4715.kl) or (4715.Kl) or 4715.KL or 4715.kl or 4715.Kl
        {
            "label": label,
            "pattern": [
                {"TEXT": "(", "OP": "*"},
                {"LOWER": f"{text}.kl"},
                {"TEXT": ")", "OP": "*"},
            ],
        },
        ## match (4715.KLS) or (4715.kls) or (4715.Kls) or 4715.KLS or 4715.kls or 4715.Kls
        {
            "label": label,
            "pattern": [
                {"TEXT": "(", "OP": "*"},
                {"LOWER": f"{text}.kls"},
                {"TEXT": ")", "OP": "*"},
            ],
        },
        ## match (4715.KLSE) or (4715.klse) or (4715.Klse) or 4715.KLSE or 4715.klse or 4715.Klse
        {
            "label": label,
            "pattern": [
                {"TEXT": "(", "OP": "*"},
                {"LOWER": f"{text}.klse"},
                {"TEXT": ")", "OP": "*"},
            ],
        },
        ## match (4715.MY) or (4715.my) or (4715.My) or 4715.MY or 4715.my or 4715.My
        {
            "label": label,
            "pattern": [
                {"TEXT": "(", "OP": "*"},
                {"LOWER": f"{text}.my"},
                {"TEXT": ")", "OP": "*"},
            ],
        },
        ## match (KL:4715) or (kl:4715) or (Kl:4715) or KL:4715 or kl:4715 or Kl:4715
        {
            "label": label,
            "pattern": [
                {"TEXT": "(", "OP": "*"},
                {"LOWER": f"kl:{text}"},
                {"TEXT": ")", "OP": "*"},
            ],
        },
        ## match (KLS:4715) or (kls:4715) or (Kls:4715) or KLS:4715 or kls:4715 or Kls:4715
        {
            "label": label,
            "pattern": [
                {"TEXT": "(", "OP": "*"},
                {"LOWER": f"kls:{text}"},
                {"TEXT": ")", "OP": "*"},
            ],
        },
        ## match (KLSE:4715) or (klse:4715) or (Klse:4715) or KLSE:4715 or klse:4715 or Klse:4715
        {
            "label": label,
            "pattern": [
                {"TEXT": "(", "OP": "*"},
                {"LOWER": f"klse:{text}"},
                {"TEXT": ")", "OP": "*"},
            ],
        },
    ]


def label_stock_symbol(label: str, text: str):
    # assuming we want to recognize this stock ticker called GENM
    text = text.lower()
    return [
        ## match (GENM) or (genm)
        {
            "label": label,
            "pattern": [{"ORTH": "("}, {"LOWER": text}, {"ORTH": ")"}],
        },
        ## match (GENM.KL) or (genm.kl) or GENM.KL or genm.kl
        {
            "label": label,
            "pattern": [
                {"ORTH": "(", "OP": "*"},
                {"LOWER": f"{text}.kl"},
                {"ORTH": ")", "OP": "*"},
            ],
        },
        ## match (Genm.KL) or (genm.KL) or Genm.KL or genm.KL
        {
            "label": label,
            "pattern": [
                {"ORTH": "(", "OP": "*"},
                {"LOWER": text},
                {"ORTH": "."},
                {"LOWER": "kl"},
                {"ORTH": ")", "OP": "*"},
            ],
        },
        ## match (GENM.KLS) or (genm.kls) or GENM.KLS or genm.kls
        {
            "label": label,
            "pattern": [
                {"ORTH": "(", "OP": "*"},
                {"LOWER": f"{text}.kls"},
                {"ORTH": ")", "OP": "*"},
            ],
        },
        ## match (Genm.KLS) or (genm.KLS) or Genm.KLS or genm.KLS
        {
            "label": label,
            "pattern": [
                {"ORTH": "(", "OP": "*"},
                {"LOWER": text},
                {"ORTH": "."},
                {"LOWER": "kls"},
                {"ORTH": ")", "OP": "*"},
            ],
        },
        ## match (GENM.MY) or (genm.my) or GENM.MY or genm.my
        {
            "label": label,
            "pattern": [
                {"ORTH": "(", "OP": "*"},
                {"LOWER": f"{text}.my"},
                {"ORTH": ")", "OP": "*"},
            ],
        },
        ## match (Genm.MY) or (genm.MY) or Genm.MY or genm.MY
        {
            "label": label,
            "pattern": [
                {"ORTH": "(", "OP": "*"},
                {"LOWER": text},
                {"ORTH": "."},
                {"LOWER": "my"},
                {"ORTH": ")", "OP": "*"},
            ],
        },
        ## match (KLS:GENM) or (kls:genm) or (KLS:genm) or KLS:GENM or kls:genm or KLS:genm
        {
            "label": label,
            "pattern": [
                {"TEXT": "(", "OP": "*"},
                {"LOWER": "kls"},
                {"TEXT": ":"},
                {"LOWER": text},
                {"TEXT": ")", "OP": "*"},
            ],
        },
        ## match (KLSE:GENM) or (klse:genm) or (KLSE:genm) or KLSE:GENM or klse:genm or KLSE:genm
        {
            "label": label,
            "pattern": [
                {"TEXT": "(", "OP": "*"},
                {"LOWER": "klse"},
                {"TEXT": ":"},
                {"LOWER": text},
                {"TEXT": ")", "OP": "*"},
            ],
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
