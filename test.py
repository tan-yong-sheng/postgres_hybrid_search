import spacy

nlp = spacy.load("project/ml_models/extract_tickers_model")

doc = nlp(
    "Based on corporate announcements and news flow on Monday, companies that may be in focus on Tuesday (Jan 4) include Malayan Banking Bhd, Serba Dinamik Holdings Bhd, AirAsia Group Bhd, Supermax Corp Bhd, Yinson Holdings Bhd, Poh Kong Holdings Bhd, Hap Seng Consolidated Bhd, Opcom Holdings Bhd, Advancecon Holdings Bhd and Pantech Group Holdings Bhd"
)

for ent in doc.ents:
    print(ent.text, ent.label_)
