# need match airasia group bhd

import pytest

text1 = """Based on corporate announcements and news flow on Monday, 
        companies that may be in focus on Tuesday (Jan 4) include 
        Malayan Banking Bhd, Serba Dinamik Holdings Bhd, AirAsia Group Bhd, 
        Supermax Corp Bhd, Yinson Holdings Bhd, Poh Kong Holdings Bhd, 
        Hap Seng Consolidated Bhd, Opcom Holdings Bhd, Advancecon Holdings Bhd 
        and Pantech Group Holdings Bhd"""
expected_match1 = [
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
    {
        "exchange": "Bursa",
        "entity_name": "AIRASIA GROUP",
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


@pytest.mark.parametrize(
    "text, expected_match",
    [
        (text1, expected_match1),
    ],
)
def test_unit_extract_financial_entities(text, expected_match):
    from project.utils.nlp_handler import extract_financial_entities

    matches = extract_financial_entities(text)
    assert matches == expected_match
