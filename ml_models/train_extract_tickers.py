import re
from pathlib import Path

import spacy

from db_connection import db_context
from db_models import StockSymbolOrm
from schemas import ExtractTicker

with db_context() as db_session:
    stock_symbols = db_session.query(StockSymbolOrm).all()
    stock_symbols = [
        ExtractTicker(**stock_symbol.__dict__) for stock_symbol in stock_symbols
    ]

# Initialize the spaCy pipeline with the entity ruler component
nlp = spacy.blank("en")
ruler = nlp.add_pipe("entity_ruler")
patterns = []

# Add stock stock_code patterns to the entity ruler
for item in stock_symbols:
    patterns.append({"label": "STOCK_CODE", "pattern": item.stock_code})
    patterns.append(
        {
            "label": "STOCK_CODE",
            "pattern": [{"TEXT": item.stock_code}, {"TEXT": ".KL"}],
        }
    )
    patterns.append(
        {
            "label": "STOCK_CODE",
            "pattern": [{"TEXT": "("}, {"TEXT": item.stock_code}, {"TEXT": ")"}],
        }
    )
    patterns.append(
        {
            "label": "STOCK_CODE",
            "pattern": [{"TEXT": "(KL:"}, {"TEXT": item.stock_code}, {"TEXT": ")"}],
        }
    )

    # Add stock symbol patterns to the entity ruler
    patterns.append({"label": "STOCK_SYMBOL", "pattern": item.stock_symbol})
    patterns.append(
        {
            "label": "STOCK_SYMBOL",
            "pattern": [{"TEXT": "(KL:"}, {"TEXT": item.stock_symbol}, {"TEXT": ")"}],
        }
    )
    patterns.append(
        {
            "label": "STOCK_SYMBOL",
            "pattern": [{"TEXT": item.stock_symbol}, {"TEXT": ":MK"}],
        }
    )  # Bloomberg

    # Add company name patterns to the entity ruler
    patterns.append({"label": "COMPANY", "pattern": item.company_name})
    patterns.append({"label": "COMPANY", "pattern": item.company_name.title()})

    # Handle BHD/BERHAD variations
    bhd_uppercase = re.sub(r"(BERHAD)$", "BHD", item.company_name)
    patterns.append({"label": "COMPANY", "pattern": bhd_uppercase})

    berhad_uppercase = re.sub(r"(BHD)$", "BERHAD", item.company_name)
    patterns.append({"label": "COMPANY", "pattern": berhad_uppercase})

    bhd_titlecase = re.sub(r"(BHD)$", "BHD", item.company_name).title()
    patterns.append({"label": "COMPANY", "pattern": bhd_titlecase})

    berhad_titlecase = re.sub(r"(BHD)$", "BERHAD", item.company_name).title()
    patterns.append({"label": "COMPANY", "pattern": berhad_titlecase})

ruler.add_patterns(patterns)


# Function to map matched entities to the original stock code or symbol
def map_entities_to_stock_codes(text, company_df):
    doc = nlp(text)
    matched_dict = {}

    # Loop through each recognized entity and map it to the corresponding stock_code or symbol
    for ent in doc.ents:
        if ent.label_ == "STOCK_CODE":
            stock_code = ent.text
            original_row = company_df[company_df["stock_code"] == stock_code]
            if not original_row.empty:
                matched_dict[stock_code] = original_row.iloc[0]["stock_code"]

        elif ent.label_ == "STOCK_SYMBOL":
            stock_symbol = ent.text
            original_row = company_df[company_df["stock_symbol"] == stock_symbol]
            if not original_row.empty:
                matched_dict[stock_symbol] = original_row.iloc[0]["stock_symbol"]

        elif ent.label_ == "COMPANY":
            company_name = ent.text
            original_row = company_df[
                company_df["company_name"].str.contains(company_name, case=False)
            ]
            if not original_row.empty:
                matched_dict[company_name] = original_row.iloc[0]["company_name"]

    return matched_dict


nlp.to_disk(path=Path(__file__).parent / "extract_tickers_model")
