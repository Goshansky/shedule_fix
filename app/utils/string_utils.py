import re


def extract_building(location):
    match = re.search(r'\((.*?)\)', location)
    return match.group(1) if match else None


def extract_campus(location):
    match = re.match(r'([А-ЯA-Z])-', location)
    return match.group(1) if match else None
