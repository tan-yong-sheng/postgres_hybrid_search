import csv


def read_csv_file(file_path: str):
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        return list(reader)


def export_to_csv(filename: str, data: list):
    with open(filename, mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"Data exported to {filename}")
