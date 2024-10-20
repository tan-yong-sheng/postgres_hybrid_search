from project.utils.csv_handler import (
    export_to_csv,  # Adjust the import according to your project structure
)


def test_integrate_export_to_csv_with_header(tmp_path):
    # integration test for csv export with header
    # Mock data
    data = iter([{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}])

    # Expected CSV content
    expected_output = "name,age\r\nBob,25\r\n"

    # Create a temporary file
    temp_file = tmp_path / "test_with_header.csv"

    # Call the function
    _ = export_to_csv(temp_file, data, header=True)

    # Read the CSV content
    with open(temp_file, mode="r", newline="") as csv_file:
        result = csv_file.read()

    # Assert the CSV content matches the expected output
    assert result == expected_output


def test_integrate_export_to_csv_without_header(tmp_path):
    # integration test for csv export with header
    # Mock data
    data = iter([{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}])

    # Expected CSV content
    expected_output = "Alice,30\r\nBob,25\r\n"

    # Create a temporary file
    temp_file = tmp_path / "test_without_header.csv"

    # Call the function
    _ = export_to_csv(temp_file, data, header=False)

    # Read the CSV content
    with open(temp_file, mode="r", newline="") as csv_file:
        result = csv_file.read()

    # Assert the CSV content matches the expected output
    assert result == expected_output
