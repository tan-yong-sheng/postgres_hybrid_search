import re

import spacy

from db_connection import db_context
from models import NewsOrm, StockSymbolOrm

with db_context() as db_session:
    company_df = db_session.query(StockSymbolOrm).all()
    news_df = db_session.query(NewsOrm).all()

# Extract company names, symbols, and stock codes into lists
companies = company_df["company_name"].to_list()
symbols = company_df["stock_symbol"].to_list()
stock_codes = company_df["stock_code"].to_list()

# Initialize the spaCy pipeline with the entity ruler component
nlp = spacy.blank("en")
ruler = nlp.add_pipe("entity_ruler")
patterns = []

# Add stock code, symbol, and company name patterns to the entity ruler
for stock_code in stock_codes:
    patterns.append({"label": "STOCK_CODE", "pattern": stock_code})
    patterns.append(
        {"label": "STOCK_CODE", "pattern": [{"TEXT": stock_code}, {"TEXT": ".KL"}]}
    )
    patterns.append(
        {
            "label": "STOCK_CODE",
            "pattern": [{"TEXT": "("}, {"TEXT": stock_code}, {"TEXT": ")"}],
        }
    )
    patterns.append(
        {
            "label": "STOCK_CODE",
            "pattern": [{"TEXT": "(KL:"}, {"TEXT": stock_code}, {"TEXT": ")"}],
        }
    )

for symbol in symbols:
    patterns.append({"label": "STOCK_SYMBOL", "pattern": symbol})
    patterns.append(
        {
            "label": "STOCK_SYMBOL",
            "pattern": [{"TEXT": "(KL:"}, {"TEXT": symbol}, {"TEXT": ")"}],
        }
    )
    patterns.append(
        {"label": "STOCK_SYMBOL", "pattern": [{"TEXT": symbol}, {"TEXT": ":MK"}]}
    )  # Bloomberg

for company in companies:
    patterns.append({"label": "COMPANY", "pattern": company})
    patterns.append({"label": "COMPANY", "pattern": company.title()})

    # Handle BHD/BERHAD variations
    bhd_uppercase = re.sub(r"(BERHAD)$", "BHD", company)
    patterns.append({"label": "COMPANY", "pattern": bhd_uppercase})

    berhad_uppercase = re.sub(r"(BHD)$", "BERHAD", company)
    patterns.append({"label": "COMPANY", "pattern": berhad_uppercase})

    bhd_titlecase = re.sub(r"(BHD)$", "BHD", company).title()
    patterns.append({"label": "COMPANY", "pattern": bhd_titlecase})

    berhad_titlecase = re.sub(r"(BHD)$", "BERHAD", company).title()
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


# Apply the mapping function to the 'long_text' column
news_df["matched_entities"] = news_df["long_text"].apply(
    lambda text: map_entities_to_stock_codes(text, company_df)
)

# The result will be a DataFrame column where each entry is a dictionary mapping the recognized entities to their original stock code or symbol
news_df[["title", "matched_entities"]]
