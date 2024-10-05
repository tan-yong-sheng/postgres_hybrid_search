from datetime import datetime, timedelta

import pandas as pd
import requests

# Define headers and session for HTTP requests

http_session = requests.Session()


def make_request(url, headers=None, **kwargs):
    default_headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    if headers:
        default_headers.update(headers)
    return http_session.get(url, headers=default_headers, cookies=kwargs.get("cookies"))


# Function to generate date ranges
def generate_date_ranges(start_date, end_date, delta_days=1):
    current_date = start_date
    while current_date <= end_date:
        start = current_date
        end = current_date + timedelta(days=delta_days) - timedelta(seconds=1)
        yield start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")
        current_date += timedelta(days=delta_days)


# Define a function to scrape news data from the KLSE screener website
def scrape_news(start_date=None, end_date=None):
    params = {}

    # Convert start_date to a datetime object if provided
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")

    # Convert end_date to a Unix timestamp if provided
    if end_date:
        end_date = int(datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S").timestamp())

    while True:
        # Make a request to the news endpoint
        url = f"https://www.klsescreener.com/v2/news/index?until={params.get('until', end_date)}"
        response = make_request(url, cookies={"news.lang": "en"})
        response.raise_for_status()  # Ensure the request was successful
        news_data = response.json()

        # Flatten the news data and yield each item
        for news_item in news_data["data"]:
            news = news_item["News"]
            created_date_str = news.get("created")
            created_date = datetime.strptime(created_date_str, "%Y-%m-%d %H:%M:%S")

            # Stop the scraping logic if created_date is smaller than start_date
            if start_date and created_date < start_date:
                return  # Stop the generator

            # Extract the content from the '0' key if it exists
            content = news_item.get("0", {}).get("content", "")
            # Extract publisher info
            publisher = news_item.get("Publisher", {})

            # Create a normalized news entry
            normalized_news = {
                "id": news.get("id"),
                "title": news.get("title"),
                "summary": news.get("summary"),
                "content": content,
                "created_date": created_date_str,
                "modified_date": news.get("modified"),
                "published_date": news.get("date_post"),
                "category": news.get("category"),
                "author": news.get("author"),
                "thumbnail_url": news.get("thumbnail_url"),
                "image_url": news.get("img_url"),
                "publisher_id": publisher.get("id"),
                "publisher_name": publisher.get("name"),
                "publisher_url": publisher.get("url"),
            }

            yield normalized_news

        # Prepare for the next page request
        if "paging" in news_data and "until" in news_data["paging"]:
            params["until"] = news_data["paging"]["until"]
        else:
            return  # Stop the generator if no more paging data is available


if __name__ == "__main__":
    import os

    os.makedirs("data/news", exist_ok=True)

    # Define the overall date range
    overall_start_date = datetime.strptime("2022-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    overall_end_date = datetime.strptime("2022-01-05 23:59:59", "%Y-%m-%d %H:%M:%S")

    # Loop over each date range and scrape news data
    for start_date, end_date in generate_date_ranges(
        overall_start_date, overall_end_date
    ):
        news_items = scrape_news(start_date=start_date, end_date=end_date)
        # Process the yielded news items and write them to a CSV
        pd.DataFrame(news_items).to_csv(f"data/news/news_{end_date}.csv", index=False)
