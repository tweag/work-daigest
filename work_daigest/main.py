import argparse
import datetime
import functools
import json
import os
import pathlib
from pickle import dump, load

from ics import Calendar
import pytz

from .bedrock import init_client, invoke_claude3, invoke_llama2, invoke_jurassic2
from .fetchers.google_calendar import format_events
from .fetchers.github import fetch_comments

PROMPT_TEMPLATE = """
    Summarize the events in the calendar and my work on GitHub and tell me what I did during the covered period of time.
    If the event has a description, include a summary.
    Include attendees names.
    If the event is lunch, do not include it.
    For GitHub issues / pull requests / commits, don't include the full text / description / commit message,
    but summarize it if it is longer than two sentences.

    Calendar events:
    ```
    {calendar_data}
    ```

    These are GitHub issues, pull requests and commits I worked on, in a JSON format:
    ```
    {github_data}
    ```
    """

def munge_calendar_data(file_path: str, min_date: datetime.datetime, max_date: datetime.datetime, email: str) -> str:
    """
    Munge calendar data to be used in the prompt template.

    :param file_path: Path to the calendar file.
    :param min_date: Minimum date to consider.
    :param max_date: Maximum date to consider.
    :param email: Email to filter calendar events.
    :return: Munged calendar data.
    """
    # Cache munged calendar data
    CACHE_FILE = "caldump.pickle"
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "rb") as f:
            cal_text = load(f)
    else:
        with open(file_path, 'r') as f:
            calendar = Calendar(f.read())

        utc = pytz.UTC
        cal_text = format_events(calendar, utc.localize(min_date), utc.localize(max_date), email)
        with open(CACHE_FILE, "wb") as f:
            dump(cal_text, f)

    return cal_text

def munge_github_data(file_path: str) -> str:
    """
    Munge GitHub data to be used in the prompt template.

    :param file_path: Path to the JSON file containing GitHub data
      as produced by the GitHub fetcher.
    :return: Munged GitHub data.
    """
    with open(file_path, 'r') as f:
        github_data = json.load(f)

    return json.dumps(github_data)

def convert_to_datetime(datestr: str) -> datetime.datetime:
    """
    Convert a date string of the format YYYY-MM-DD to a datetime object
    and augment with one milliseconds to make it compatible with the GitHub
    API.
    """
    return datetime.datetime.strptime(datestr, "%Y-%m-%d").replace(microsecond=1)


def main():
    """
    Main program flow.
    """
    parser = argparse.ArgumentParser(description="Generate a summary of your work")
    parser.add_argument("--calendar-data", type=pathlib.Path, help="Path to the calendar .ics file", required=True)
    parser.add_argument("--github-handle", type=str, help="GitHub handle to use when fetching GitHub data", required=True)
    parser.add_argument("--email", type=str, help="Email address to use when filtering calendar events", required=True)
    parser.add_argument("--lower-date", type=convert_to_datetime, help="Lower date limit to consider data for, in the format YYYY-MM-DD. Defaults to today - 7 days.", default=(datetime.datetime.today() - datetime.timedelta(days=7)).strftime("%Y-%m-%d"))
    parser.add_argument("--upper-date", type=convert_to_datetime, help="Upper date limit to consider data for, in the format YYYY-MM-DD. Defaults to today.", default=datetime.datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--model", type=str, choices=["jurassic2", "llama2", "claude3"], default="claude3", help="Model to use for summary generation")
    args = parser.parse_args()

    runtime_client = init_client('bedrock-runtime', 'us-east-1')

    match args.model:
        case "jurassic2":
            model_invocation_fn = functools.partial(invoke_jurassic2, client=runtime_client)
        case "llama2":
            model_invocation_fn = functools.partial(invoke_llama2, client=runtime_client)
        case "claude3":
            model_invocation_fn = functools.partial(invoke_claude3, client=runtime_client)
        case _:
            # should never occur due to the choices limitation in the argument parser
            raise ValueError("Invalid model")

    calendar_data = munge_calendar_data(args.calendar_data, args.lower_date, args.upper_date, args.email)
    github_data = fetch_comments(args.github_handle, args.lower_date, args.upper_date)

    res = model_invocation_fn(prompt=PROMPT_TEMPLATE.format(calendar_data=calendar_data, github_data=github_data))
    print(res)


if __name__ == "__main__":
    main()