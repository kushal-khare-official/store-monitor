import csv


def save_report(file_name, report_data):
    header = [
        "store_id",
        "uptime_last_hour(in minutes)",
        "uptime_last_day(in hours)",
        "update_last_week(in hours)",
        "downtime_last_hour(in minutes)",
        "downtime_last_day(in hours)",
        "downtime_last_week(in hours)",
    ]
    row_list = [header] + report_data

    with open(f"reports/{file_name}", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(row_list)
