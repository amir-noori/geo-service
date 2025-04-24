from datetime import datetime


def str_to_date(date_string: str, date_format: str = "%Y-%m-%d"):
    return datetime.strptime(date_string, date_format)

def date_to_str(date, date_format: str = "%Y-%m-%d"):
    return date.strftime(date_format)