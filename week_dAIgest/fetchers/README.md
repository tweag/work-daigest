# Data fetchers

## GitHub

The GitHub fetcher gets
- issue descriptions,
- PR descriptions,
- commit messages

from both public and private repos. It expects a (classic) GitHub personal token in the environment variable `GITHUB_TOKEN`. That token needs to have the full `repo` OAuth scopes.
Adapt the GitHub user handle / lower / upper date / time limits in the code as needed.

Run it like so:
```console
$ GITHUB_TOKEN=<token> python github.py > github_data.json
```

This will produce a file `github_data.json` which can be consumed by the main application's `--github-data` argument.

## Google Calendar

The fetcher is currently you :-)
For now, you'll have to get a manual calendar data dump as described in `../../README.md`.
The file `google_calendar.py` contains code to munge that manually-obtained data and is called from the main application.
