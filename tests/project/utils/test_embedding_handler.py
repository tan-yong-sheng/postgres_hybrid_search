import json
from pathlib import Path


def mock_output(return_value=None):
    return lambda *args, **kwargs: return_value


def test_unit_get_embedding(monkeypatch):
    from project.utils import embedding_handler

    return_value = [0] * 384
    monkeypatch.setattr(embedding_handler, "get_embedding", mock_output(return_value))

    result = embedding_handler.get_embedding("Hello, world!")
    assert result == [0] * 384


def test_integrate_get_embedding():
    from project.utils import embedding_handler

    input = "Hello, world!"
    expected_output = json.load(
        open(Path(__file__).parent / "embedding_output.json", "r")
    )
    # Call the function to test
    result = embedding_handler.get_embedding(input)
    # Assert the result matches the expected output
    assert result == expected_output
    assert len(result["data"][0]["embedding"]) == 384
