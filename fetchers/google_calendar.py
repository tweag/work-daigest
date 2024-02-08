from ics import Calendar
from datetime import datetime
import pytz
import re


calendar_file = 'calendar.ics'
# email of the person owning the calendar
email = ""
d1 = datetime(2024, 1, 29, tzinfo=pytz.timezone("CET"))
d2 = datetime(2024, 2, 4, tzinfo=pytz.timezone("CET"))


def remove_text_pattern(description):
    pattern = r"-::~:~::~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~::~:~::-[\s\S]+-::~:~::~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~:~::~:~::-"
    # remove the pattern from the description
    return re.sub(pattern, '', description)


def extract_events(calendar: Calendar, start: datetime, end: datetime):
    events = calendar.events
    events = [e for e in events if e.begin >= start and e.end <= end]
    go_to_next = False
    for e in events:
        event_text = []
        for att in e.attendees:
            if att.email == email and att.partstat == "DECLINED" or att.partstat == "NEEDS-ACTION":
                go_to_next = True
        if go_to_next:
            go_to_next = False
            continue
        event_text.append(e.name)
        for att in e.attendees:
            if att.email == email:
                event_text.append(f"status: {att.partstat}")

        event_text.append(f"start: {e.begin}")
        event_text.append(f"end: {e.end}")
        event_text.append(f"duration: {e.duration}")

        if desc := e.description:
            desc = remove_text_pattern(desc)
            event_text.append(f"description: {desc}")

        if e.location:
            event_text.append(f"location: {e.location}")

        if e.attendees:
            event_text.append("attendees:")
        for att in e.attendees:
            event_text.append(f"  - {att.common_name}")

        event_text.append("-------------------")
        print("\n".join(event_text))


def main():
    with open(calendar_file, 'r') as f:
        print("Reading calendar from file")
        calendar = Calendar(f.read())

    print("Extracting events from calendar")
    extract_events(calendar, d1, d2)


if __name__ =="__main__":
    main()