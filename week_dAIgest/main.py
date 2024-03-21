import datetime
import json
import os
from pickle import dump, load

from .bedrock import init_client, invoke_claude3, invoke_llama2, invoke_jurassic2
from .fetchers.google_calendar import format_events

from ics import Calendar

model_name = "meta.llama2-70b-chat-v1"
#model_name = "ai21.j2-jumbo-instruct"

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

        cal_text = format_events(calendar, min_date, max_date, email)
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

github_data = munge_github_data("github_data.json")
calendar_data = munge_calendar_data("calendar.ics", datetime.datetime.now() - datetime.timedelta(days=60), datetime.datetime.now(), "simeon.carstens@tweag.io")

runtime_client = init_client('bedrock-runtime', 'us-east-1')

prompt_template = f"""
    My name is Simeon Carstens and I am a software engineer at Tweag.
    Summarize the events in the calendar and my work on GitHub and tell me what I did this week.
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
    {json.dumps(github_data)}
    ```
    """

# res = invoke_llama2(runtime_client, model_id=model_name, prompt=prompt_template)
# res = invoke_jurassic2(runtime_client, jurassic_model=model_name, prompt=prompt_template)
res = invoke_claude3(runtime_client, prompt=prompt_template)
print(res)
