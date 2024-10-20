import csv
from typing import Iterable


def read_csv_file(file_path: str):
    with open(file_path, "r") as file:
        reader = csv.DictReader(file, quotechar='"', delimiter=",")
        return list(reader)


def export_to_csv(filename: str, data: Iterable[list[dict]], header: bool = True):
    with open(filename, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file, quotechar='"', delimiter=",")

        if header is True:
            header_data = next(data)
            writer.writerow(header_data.keys())
        for row in data:
            writer.writerow(row.values())
    print(f"Data exported to {filename}")
