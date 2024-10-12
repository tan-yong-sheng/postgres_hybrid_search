from datetime import timedelta


# Function to generate date ranges
def generate_date_ranges(start_date, end_date, delta_days=1):
    current_date = start_date
    while current_date <= end_date:
        start = current_date
        end = current_date + timedelta(days=delta_days) - timedelta(seconds=1)
        yield start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")
        current_date += timedelta(days=delta_days)
