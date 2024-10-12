TEXT = """Based on corporate announcements and news flow on Monday, 
        companies that may be in focus on Tuesday (Jan 4) include 
        Malayan Banking Bhd, Serba Dinamik Holdings Bhd, AirAsia Group Bhd, 
        Supermax Corp Bhd, Yinson Holdings Bhd, Poh Kong Holdings Bhd, 
        Hap Seng Consolidated Bhd, Opcom Holdings Bhd, Advancecon Holdings Bhd 
        and Pantech Group Holdings Bhd"""


def test_extract_financial_entities():
    from project.utils.nlp_handler import extract_financial_entities

    matches = extract_financial_entities(TEXT)
    print(matches)

    assert matches == [
        {
            "exchange": "Bursa",
            "entity_name": "MALAYAN BANKING",
            "entity_type": "COMPANY_NAME",
        },
        {
            "exchange": "Bursa",
            "entity_name": "SERBA DINAMIK HOLDINGS",
            "entity_type": "COMPANY_NAME",
        },
        {"exchange": "Bursa", "entity_name": "SUPERMAX", "entity_type": "COMPANY_NAME"},
        {
            "exchange": "Bursa",
            "entity_name": "YINSON HOLDINGS",
            "entity_type": "COMPANY_NAME",
        },
        {
            "exchange": "Bursa",
            "entity_name": "POH KONG HOLDINGS",
            "entity_type": "COMPANY_NAME",
        },
        {
            "exchange": "Bursa",
            "entity_name": "HAP SENG CONSOLIDATED",
            "entity_type": "COMPANY_NAME",
        },
        {
            "exchange": "Bursa",
            "entity_name": "ADVANCECON HOLDINGS",
            "entity_type": "COMPANY_NAME",
        },
        {
            "exchange": "Bursa",
            "entity_name": "PANTECH GROUP HOLDINGS",
            "entity_type": "COMPANY_NAME",
        },
    ]
