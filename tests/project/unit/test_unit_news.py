from datetime import datetime

import pytest
from pydantic import ValidationError

from project.schemas.news_schema import NewsCreate


def test_unit_schema_news_validation():
    valid_data = {
        "created_at": "2022-01-01 00:00:00",
        "updated_at": "2022-01-01 00:00:00",
        "title": "Genting Malaysia Berhad gets a new contract",
        "content": "Genting Malaysia Berhad has secured a new contract to build a new casino in Malaysia.",
        "url": "https://www.gentingmalaysia.com/",
    }

    news = NewsCreate(**valid_data)
    assert news.created_at == datetime(2022, 1, 1, 0, 0, 0)
    assert news.updated_at == datetime(2022, 1, 1, 0, 0, 0)
    assert news.title == "Genting Malaysia Berhad gets a new contract"
    assert (
        news.content
        == "Genting Malaysia Berhad has secured a new contract to build a new casino in Malaysia."
    )
    assert news.url == "https://www.gentingmalaysia.com/"

    with pytest.raises(ValidationError):
        invalid_data = {"created_at": "2022-01-01 00:00:00"}
        NewsCreate(**invalid_data)
