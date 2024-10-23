from project.utils.csv_handler import (  # Adjust the import according to your project structure
    export_iterable_to_csv,
    export_list_to_csv,
)


def test_export_list_to_csv_with_header(tmp_path):
    # Mock data
    data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
    ]

    # Expected CSV content
    expected_output = "name,age\r\nAlice,30\r\nBob,25\r\n"

    # Create a temporary file
    temp_file = tmp_path / "test_with_header.csv"

    # Call the function
    _ = export_list_to_csv(temp_file, data, header=True)

    # Read the CSV content
    with open(temp_file, mode="r", newline="") as csv_file:
        result = csv_file.read()

    # Assert the CSV content matches the expected output
    assert result == expected_output


def test_export_list_to_csv_without_header(tmp_path):
    # Mock data
    data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
    ]

    # Expected CSV content
    expected_output = "Alice,30\r\nBob,25\r\n"

    # Create a temporary file
    temp_file = tmp_path / "test_without_header.csv"

    # Call the function
    _ = export_list_to_csv(temp_file, data, header=False)

    # Read the CSV content
    with open(temp_file, mode="r", newline="") as csv_file:
        result = csv_file.read()

    # Assert the CSV content matches the expected output
    assert result == expected_output


def test_export_list_to_csv_empty_data(tmp_path):
    # Mock data
    data = []

    # Expected CSV content
    expected_output = ""

    # Create a temporary file
    temp_file = tmp_path / "test_empty_data.csv"

    # Call the function
    _ = export_list_to_csv(temp_file, data, header=False)

    # Read the CSV content
    with open(temp_file, mode="r", newline="") as csv_file:
        result = csv_file.read()

    # Assert the CSV content matches the expected output
    assert result == expected_output


def test_integrate_export_iterable_to_csv_with_header(tmp_path):
    # integration test for csv export with header
    # Mock data
    data = iter([{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}])

    # Expected CSV content
    expected_output = "name,age\r\nBob,25\r\n"

    # Create a temporary file
    temp_file = tmp_path / "test_with_header.csv"

    # Call the function
    _ = export_iterable_to_csv(temp_file, data, header=True)

    # Read the CSV content
    with open(temp_file, mode="r", newline="") as csv_file:
        result = csv_file.read()

    # Assert the CSV content matches the expected output
    assert result == expected_output


def test_integrate_export_iterable_to_csv_without_header(tmp_path):
    # integration test for csv export with header
    # Mock data
    data = iter([{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}])

    # Expected CSV content
    expected_output = "Alice,30\r\nBob,25\r\n"

    # Create a temporary file
    temp_file = tmp_path / "test_without_header.csv"

    # Call the function
    _ = export_iterable_to_csv(temp_file, data, header=False)

    # Read the CSV content
    with open(temp_file, mode="r", newline="") as csv_file:
        result = csv_file.read()

    # Assert the CSV content matches the expected output
    assert result == expected_output


def test_integrate_export_iterable_to_csv_empty_data(tmp_path):
    # integration test for csv export with header
    # Mock data
    data = iter([])

    # Expected CSV content
    expected_output = ""

    # Create a temporary file
    temp_file = tmp_path / "test_empty_data.csv"

    # Call the function
    _ = export_iterable_to_csv(temp_file, data, header=False)

    # Read the CSV content
    with open(temp_file, mode="r", newline="") as csv_file:
        result = csv_file.read()

    # Assert the CSV content matches the expected output
    assert result == expected_output
