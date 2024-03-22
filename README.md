# Summarize your work week using LLMs

This project came into existence as part of an Tweag-internal hackathon on GenAI topics.
The goal is to summarize your work week using data from multiple work-related source, such as
- GitHub,
- Google Calendar,
- Slack,
- Jira,
- ...

Right now, supported data sources are GitHub and Google Calendar.

## Getting the data

### GitHub data

To get the GitHub data (issues, PRs, commits) in the expected format, use the GitHub fetcher in `weekly_dAIgest/fetchers/github.py`, following instructions in TODO [GitHub fetcher README].

### Google Calendar data

Currently, Google Calendar data needs to be exported manually into an `.ics` file.
To do that, open Google Calendar in your browser, then go to "Settings" (the cogwheel symbol) -> "Import & export" and click the "Export" button.
This downloads a zipped `.ics` file, which you will have to unpack.

## Usage

Note that the application currently calls out to [AWS Bedrock](https://aws.amazon.com/bedrock/) for LLM access.
So you'll have to enable the relevant models (default is Claude-3 Sonnet) in Bedrock and make sure that you have AWS credentials with all necessary permissions set up, for example using `aws sso configure` and `aws sso login`.
Don't forget to set the `AWS_PROFILE` environment variable to your AWS profile name if it's not the default.

To get started, install the program in a virtual environment using `nix-shell` if you're a Nix person.
If you're not, you'll have to have [Poetry](https://python-poetry.org/) installed.
Then, you can just run `poetry install` to install the application and all required dependencies and you're ready to go.

Run `weekly-dAIgest --help` to learn about the supported command line arguments:
```console
$ weekly-dAIgest --help
usage: weekly-dAIgest [-h] --calendar-data CALENDAR_DATA --email EMAIL --github-data
                      GITHUB_DATA [--model {jurassic2,llama2,claude3}]

Generate a summary of your work week

options:
  -h, --help            show this help message and exit
  --calendar-data CALENDAR_DATA
                        Path to the calendar .ics file
  --email EMAIL         Email address to use when filtering calendar events
  --github-data GITHUB_DATA
                        Path to the GitHub data file
  --model {jurassic2,llama2,claude3}
                        Model to use for summary generation
```
