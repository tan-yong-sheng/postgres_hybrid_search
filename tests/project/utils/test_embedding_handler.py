import json
from pathlib import Path

from project.utils.embedding_handler import get_embedding


def test_integrate_get_embedding():
    input = "Hello, world!"
    expected_output = json.load(
        open(Path(__file__).parent / "embedding_output.json", "r")
    )
    # Call the function to test

    result = get_embedding(input)
    # Assert the result matches the expected output
    assert result == expected_output
    assert len(result["data"][0]["embedding"]) == 384
