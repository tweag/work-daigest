from datetime import datetime
import os
from pickle import dump, load

from .bedrock import init_client, invoke_claude3, invoke_llama2, invoke_jurassic2
from .fetchers.google_calendar import format_events

from ics import Calendar
import pytz

model_name = "meta.llama2-70b-chat-v1"
#model_name = "ai21.j2-jumbo-instruct"

if os.path.exists("caldump.pickle"):
    with open("caldump.pickle", "rb") as f:
        cal_text = load(f)
else:
    calendar_file = 'calendar.ics'
    email = "simeon.carstens@tweag.io"
    d1 = datetime(2024, 1, 29, tzinfo=pytz.timezone("CET"))
    d2 = datetime(2024, 2, 4, tzinfo=pytz.timezone("CET"))

    with open(calendar_file, 'r') as f:
        print("Reading calendar from file")
        calendar = Calendar(f.read())

    cal_text = format_events(calendar, d1, d2, email)
    with open("caldump.pickle", "wb") as f:
        dump(cal_text, f)

import json
github_data = json.load(open("github_data.json"))

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
    {cal_text}
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
