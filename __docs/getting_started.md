
1. Setting up virtual environment

```
python -m virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Setting up database: `python -m project.db_models`

3. `python -m project.tasks.scrape_tickers`

4. `python -m project.tasks.insert_tickers_db`

5. `python -m project.tasks.scrape_news`

6. `python -m project.tasks.insert_news_db`

7. `python -m project.ml_models.train_extract_tickers`

8. `python -m project.tasks.insert_news_to_tickers_db`

9. `python -m project.tasks.insert_news_embedding_db`

10. `python -m project.tasks.search_news`