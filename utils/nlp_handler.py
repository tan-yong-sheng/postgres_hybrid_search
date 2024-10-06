import spacy

# Load the pre-trained spaCy model (you can use 'en_core_web_sm' or a larger model)
nlp = spacy.load("ml_models/extract_tickers_model")

company_names = [
    "4715",
    "(4715)",
    "3182",
    "(3182)",
    "(3182.KL)",
    "GENTING.KL",
    "(GENTING)",
    "4715.KL",
    "4715.KLS",
    "4715.MY",
    "4715.KLSE",
    "GENTING BERHAD",
    "Genting Berhad",
    "genting berhad",
    "genting bhd",
    "genting BHD",
    "GENTING BHD",
    "Genting Bhd",
    "GENM",
    "GENM.KL and GENM.KLS",
    "GENM.KLS",
    "GENM.MY",
    "genm.kl",
    "KLSE:GENM",
    "kls:genm",
    "Genting Malaysia Berhad",
    "GENTING MALAYSIA BERHAD",
    "Genting Malaysia Bhd",
    "Sime Darby Berhad",
    "Sime Darby",
    "(Axiata Group Bhd)",
    "(CIMB Group Holdings Bhd)",
    "PETALING JAYA: Greatech Technology Bhd is targeting to secure RM647mil in new orders for the remainder of this year. The automation solution provider has an order book of RM610mil, which can last until the first half of 2024, according to UOB Kay Hian (UOBKH) Research. It said Greatech had secured RM72mil worth of new orders from its life science customers, on top of the strong traction from its US incumbent solar customer following its massive expansion plans in Ohio, India and Alabama. The research house said 59% of the current order book came from solar and 24% from electric vehicle customers. The rest were contributed by life science (16%) and semiconductor automation (1%).",
]

# Test the NER on an example text
for name in company_names:
    doc = nlp(
        f"{name} is a leading multinational corporation with a diversified portfolio of businesses."
    )
    for ent in doc.ents:
        print(ent.text, ent.label_)