import argparse
import datetime
import functools
import json
import pathlib
from typing import List

import pytz
from ics import Calendar
from streamlit.runtime.uploaded_file_manager import UploadedFile

from .bedrock import init_client, invoke_claude3, invoke_jurassic2, invoke_llama2
from .fetchers.github import fetch_comments
from .fetchers.google_calendar import filter_events

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

def munge_calendar_data(cal_file: str | UploadedFile, min_date: datetime.datetime, max_date: datetime.datetime, email: str) -> List[str]:
    """
    Munge calendar data to be used in the prompt template.

    :param cal_file: Path to the calendar file or uploaded file.
    :param min_date: Minimum date to consider.
    :param max_date: Maximum date to consider.
    :param email: Email to filter calendar events.
    :return: Munged calendar data.
    """
    if isinstance(cal_file, UploadedFile):
        file_content = cal_file.getvalue().decode("utf-8")
    elif isinstance(cal_file, str):
        with open(cal_file, 'r') as f:
            file_content = f.read()
    else:
        raise ValueError(f"Invalid file type: {type(file_path)}")
    calendar = Calendar(file_content)

    utc = pytz.UTC
    events = filter_events(calendar, utc.localize(min_date), utc.localize(max_date), email)

    return events

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


def process_data(calendar_file, github_handle, email, lower_date, upper_date, model_choice):
    runtime_client = init_client('bedrock-runtime', 'us-east-1')
    model_functions = {
        "jurassic2": functools.partial(invoke_jurassic2, client=runtime_client),
        "llama2": functools.partial(invoke_llama2, client=runtime_client),
        "claude3": functools.partial(invoke_claude3, client=runtime_client)
    }
    
    model_fn = model_functions.get(model_choice)

    if model_fn is None:
        raise ValueError(f"Invalid model choice: {model_choice}. Choose from {model_functions.keys()}.")
        
    calendar_data = munge_calendar_data(calendar_file, lower_date, upper_date, email)
    github_data = fetch_comments(github_handle, lower_date, upper_date)
    
    return model_fn, calendar_data, github_data


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
    
    model_fn, calendar_data, github_data = process_data(args.calendar_data, args.github_handle, args.email, args.lower_date, args.upper_date, args.model)
    summary = model_fn(prompt=PROMPT_TEMPLATE.format(calendar_data='\n'.join(calendar_data), github_data=github_data))

    print(summary)


if __name__ == "__main__":
    main()
