# Building Vector Search for Financial News with SQLAlchemy and PostgreSQL

Coding environment: Linux in Github Codespaces (Note: Please read the setup guide at https://www.tanyongsheng.com/note/building-vector-search-for-financial-news-with-sqlalchemy-and-postgresql/ for more details)

1. copy `.env.sample` file to `.env` via typing this into terminal `cp .env.sample .env`, and then change the environment variables yourselves

2. Set up the Cloudflare AI gateway, as we're going to use its embedding API. See [this guide](https://developers.cloudflare.com/ai-gateway/get-started/?_gl=1*uflu3q*_gcl_au*NjcxMDgzMDguMTc0NzAxMzYyOA..*_ga*ODYzMmM0YzItMGVkYy00MmU5LThkOGMtN2QwNDU5NmM1ZmUy*_ga_SQCRB0TXZW*czE3NTIzMTU3ODMkbzEkZzEkdDE3NTIzMTU3ODkkajU0JGwwJGgw) to know how to setup AI Gateway to fill in `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_KEY` and `CLOUDFLARE_GATEWAY_ID` in our .env file.

3. Setting up virtual environment

```bash
pip install uv
uv init
uv venv
source .venv/bin/activate
uv sync
```

To export the `uv` packages to `requirements.txt`:
```bash
uv export > requirements.txt
```

4. Creating PostgreSQL instances via docker `docker compose up -d`

5. Setting up database: `python -m project.db_models`

6. Scrape stock tickers: `python -m project.tasks.scrape_tickers`

7. Insert stock tickers into database `python -m project.tasks.insert_tickers_db`

8. Scrape news: `python -m project.tasks.scrape_news --start-date="2025-01-01 00:00:00" --end-date="2025-07-11 23:59:59"`

9. Insert news into database: `python -m project.tasks.insert_news_db --start-date="2025-01-01 00:00:00" --end-date="2025-07-11 23:59:59"`

10. Train a spacy model to recognize stock codes, stock symbols, and company name from news text: `python -m project.ml_models.train_extract_tickers`

11. Recognize stock codes, stock symbols, and company name from news text using trained spacy model: `python -m project.tasks.recognize_financial_entities --start-date="2025-01-01 00:00:00" --end-date="2025-07-11 23:59:59"`

12. Then insert those records into the database table: `python -m project.tasks.insert_news_to_tickers_db --start-date="2025-01-01 00:00:00" --end-date="2025-07-11 23:59:59"`

13. Insert embeddings into database: `python -m project.tasks.insert_news_embedding_db`

14. Perform search for relevant news:
- Full text search: `python -m project.tasks.full_text_search_news`
- Vector search: `python -m project.tasks.vector_search_news`
- Hybrid search: `python -m project.tasks.hybrid_search_news`

## Building MCP

1. Running the MCP server locally
```bash
python -c "from project.mcp.stock_news_mcp import create_server; create_server().run(transport='sse')"
```

## Additional note:

For `project/tasks/scrape_tickers.py`, `project/tasks/insert_news_db.py`, `project/tasks/recognize_financial_entities` & `project/tasks/insert_news_to_tickers_db.py`, please feel free to change the start_date and end_date in the terminal shell, so that you could scrape the data accordingly.

Btw, this is just a simple prototype project. Thanks for reading, and hope for more suggestions. And please let me know if you spot any errors.

## Tips
Besides Github Codespaces, you could also try to use GitPod so you could start your coding environment very quickly: https://gitpod.io/#https://github.com/tan-yong-sheng/postgres_hybrid_search (Note: I'm not affiliate with GitPod, and the free plan gives you 50 hours per month at no cost as of 30 Sep 2024.)

This blog has two companion blogs which are Use Cases of (1) [Building Trigram Search for Stock Tickers with Python SQLAlchemy and PostgreSQL](https://www.tanyongsheng.com/note/building-trigram-search-for-stock-tickers-with-python-sqlalchemy-and-postgresql/) and (2) [Name Entity Recognition (NER) with Spacy](https://www.tanyongsheng.com/note/use-cases-of-name-entity-recognition-ner-with-spacy/).
