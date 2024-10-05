import csv


def read_csv_file(file_path: str):
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        return list(reader)
