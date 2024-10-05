import itertools
import os
import re

import pandas as pd
import requests


def initialize_session_and_url(exchange: str):
    url = ""
    if exchange == "Bursa":
        url = "https://klse.i3investor.com/wapi/web/stock/listing/datatables"
    elif exchange == "SGX":
        url = "https://sgx.i3investor.com/wapi/web/stock/listing/datatables"

    return requests.Session(), url


def fetch_data(session, url):
    json_obj = {
        "dtDraw": 1,
        "start": 0,
        "order": [{"column": 1, "dir": "asc"}],
        "page": 0,
        "size": 100,
        "marketList": [],
        "sectorList": [],
        "subsectorList": [],
        "type": "",
        "stockType": "",
    }

    data_list = []
    retries = 2

    while True:
        response = session.post(url, json=json_obj)

        if response.status_code != 200:
            if response.status_code in [429, 500, 502, 503, 504]:
                continue
            else:
                for _ in range(retries):
                    response = session.post(url, json=json_obj)
                    if response.status_code == 200:
                        break

        output = response.json().get("data", [])
        if not output:
            break
        data_list.append(output)

        json_obj["dtDraw"] += 1
        json_obj["start"] += 100
        json_obj["page"] += 1

    return data_list


def process_data(exchange, data_list):
    list_2d = list(itertools.chain.from_iterable(data_list))
    df = pd.DataFrame(list_2d)

    df = df[[13, 1, 14, 15, 10, 9, 2, 3, 4, 5, 6, 7]]
    df.columns = [
        "stock_symbol",
        "company_name",
        "stock_code",
        "sector",
        "subsector",
        "mkt",
        "open",
        "last",
        "chg%",
        "chg",
        "vol",
        "mkt_cap",
    ]
    df.drop(columns=["open", "last", "chg%", "vol", "mkt_cap"], inplace=True)

    df["company_name"] = df["company_name"].apply(
        lambda text: re.findall("<br[/]>([a-zA-Z0-9\\-\\s.()&]+)<\\/div>", text)
    )
    df["stock_code"] = df["stock_code"].astype(str)
    df = df.explode("company_name")

    df["exchange"] = exchange

    return df


def scrape_ticker_list(exchange: str, output_file: str):
    session, url = initialize_session_and_url(exchange)
    data_list = fetch_data(session, url)
    df = process_data(exchange, data_list)
    df.to_csv(output_file, index=False)


if __name__ == "__main__":
    os.makedirs("data/symbols", exist_ok=True)

    scrape_ticker_list("Bursa", "data/symbols/bursa_stock_list.csv")
