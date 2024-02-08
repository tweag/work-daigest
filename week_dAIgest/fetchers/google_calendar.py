from ics import Calendar
import re
from datetime import datetime

def remove_text_pattern(description):
    pattern = r"-::~:~::~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~::~:~::-[\s\S]+-::~:~::~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~::~:~::-"
    # remove the pattern from the description
    return re.sub(pattern, '', description)


def extract_formatted_events(calendar_file, d1, d2, email):
    with open(calendar_file, 'r') as f:
        print("Reading calendar from file")
        calendar = Calendar(f.read())

    print("Extracting events from calendar")
    return format_events(calendar, d1, d2, email)


def format_events(calendar: Calendar, start: datetime, end: datetime, email):
    events = calendar.events
    events = [e for e in events if e.begin >= start and e.end <= end]
    go_to_next = False
    all_events = []
    for e in events:
        event_text = []
        for att in e.attendees:
            if att.email == email and att.partstat == "DECLINED" or att.partstat == "NEEDS-ACTION":
                go_to_next = True
        if go_to_next:
            go_to_next = False
            continue
        event_text.append(e.name)

        event_text.append(f"duration: {e.duration}")

        if desc := e.description:
            desc = remove_text_pattern(desc)
            event_text.append(f"description: {desc}")

        if e.attendees:
            event_text.append("attendees:")
        for att in e.attendees:
            event_text.append(f"  - {att.common_name}")

        event_text.append("-------------------")
        all_events.append("\n".join(event_text))
    return "\n".join(all_events)