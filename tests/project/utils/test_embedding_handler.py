from pathlib import Path
import json
from project.utils.embedding_handler import get_embedding




def mock_output(return_value=None):
    return lambda *arg, **kwargs: return_value


def test_integrate_get_embedding():


    input = "Hello, world!"
    expected_output = json.load(
        open(Path(__file__).parent / "embedding_output.json", "r")
    )

    result = get_embedding(input)
    print(result)

    print("===================1")

    # Assert the result matches the expected output
    assert result == expected_output
    assert len(result["data"][0]["embedding"]) == 384
