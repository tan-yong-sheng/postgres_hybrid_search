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
    "(KLSE:RHBBANK)",
    "RHBBANK.KL",
    "(RHBBANK.KL)",
    "RHB Bank Berhad (RHBBANK) and Public Bank Berhad (PBBANK) are among the top gainers on Bursa Malaysia today.",
    "S P Setia Bhd (KL:SPSETIA) has officially launched its latest Australian project, Atlas Melbourne, at a preview event held at the Setia International Centre in KL Eco City on Saturday.",
    "Boustead Properties Bhd, under its Mutiara Spaces brand, has launched a new mobile app — Mutiara X Super App — on Thursday.",
    "KUALA LUMPUR: Global Infrastructure Partners is not expected to interfere with the daily operations of Malaysia Airports Holdings Bhd (MAHB) after acquiring a 30 per cent stake in it together with Abu Dhabi Investment Authority (ADIA), an analyst said.",
    "Here is a brief recap of some business news and corporate announcements that made headlines on Friday: HeiTech Padu Bhd (KL:HTPADU) said it is unaware of any corporate development that caused the unusual market activity (UMA) in its shares which spiked to a record high. HeiTech received the UMA query from Bursa Malaysia after its shares surged by as much as 56 sen, or 15.34%, to a record high of RM4.21. The stock pared some gains to close at RM4.10, still up by 45 sen or 12.33%, making it the second-highest gainer on the stock exchange in terms of value. — HeiTech Padu says unaware of reason for unusual market activity as shares rally past RM4 for first time. Privately owned rail construction company Dhaya Maju Infrastructure (Asia) Sdn Bhd is taking up a 57.52% stake in Pestech International Bhd (KL:PESTECH) for RM160 million through a restricted issue. Pestech had entered into a conditional subscription agreement with Dhaya Maju for the subscription of 1.34 billion restricted shares at 12 sen apiece, totalling RM160 million. Dhaya Maju and the parties acting in concert intend to apply to the Securities Commission Malaysia for an exemption from the obligation to undertake a mandatory general offer. — Dhaya Maju to acquire 57.52% stake in Pestech for RM160 mil or 12 sen per share.Velesto Energy Bhd (KL:VELESTO) has inked a MOU for a three-year collaboration with SLB, formerly Schlumberger, to enhance its rig capabilities. The rigs will incorporate well delivery solutions and drilling emissions management solutions from SLB to enhance and optimise its drilling performance and monitor emissions. — Velesto to further enhance rig capabilities via collaboration with SLB. OCR Group Bhd (KL:OCR) is suing Kumpulan Jetson Bhd (KL:JETSON) over alleged breaches of a RM88.03 million contract to build four blocks of serviced apartments in Jalan Yap Kwan Seng, Kuala Lumpur. The property developer said the lawsuit was filed at the High Court on Thursday by its 50.01%-owned unit O&C Makok Isola Sdn Bhd (OCMI) against Kumpulan Jetson and and its wholly owned subsidiary Jetson Construction Sdn Bhd (JCSB). — OCR sues Kumpulan Jetson over alleged breach of RM88 mil construction contract. Renewable energy company Solar District Cooling Group Bhd (KL:SDCG) plans to expand its solar and energy efficiency services into Brunei. Its wholly owned subsidiary, Solar District Cooling Sdn Bhd, has entered into a MOU with Brunei-based Serikandi Oil Field Services Sdn Bhd to explore collaboration opportunities that will cover the provision and maintenance of building management systems, gas-fired chillers and chilled water systems. — Solar District Cooling plans to expand energy services into Brunei. EG Industries Bhd (KL:EG) is acquiring a 24.08% stake in Thai-based ND Rubber Public Company Ltd (NDR) for 198 million baht (RM26.05 million) as part of its expansion into the 5G photonics and embedded electric vehicle (EV) market in that country. EG Industries plans to establish a testing centre for EV 5G photonics modules in Thailand that will be set up by its newly formed subsidiary, Xtronic Co Ltd. — EG Industries buys 24% stake in Thai-based tyre maker for RM26 mil. Precision plastic injection moulding manufacturer Sanichi Technology Bhd (KL:SANICHI) has proposed to consolidate its shares on a 10-to-one basis. It also proposed a capital reduction of up to RM55 million from its issued share capital to offset its accumulated losses of RM93.93 million at the group level as of June 30, 2024 (1QFY2024). — Sanichi proposes 10-to-one share consolidation, capital reduction. Construction firm Aneka Jaringan Holdings Bhd (KL:ANEKA) has aborted its planned private placement of up to 10% of its issued share capital, which was intended to raise up to RM15.51 million. It said the extension period to complete the private placement will lapse after Oct 5. Meanwhile, MyTech Group Bhd (KL:MYTECH) has also called off its planned private placement, which was announced on March 18 last year, as the deadline to implement the corporate exercise lapsed on Friday. — Aneka Jaringan and MyTech abort private placements as deadlines lapse",
]

# Test the NER on an example text
for name in company_names:
    doc = nlp(name)
    for ent in doc.ents:
        print(ent.text, ent.label_)
    print("---------------")
