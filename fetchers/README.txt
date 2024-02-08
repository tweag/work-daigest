## Data fetchers

### GitHub

The GitHub fetcher gets
- issue descriptions,
- PR descriptions,
- commit messages

from both public and private repos. It expects a (classic) GitHub personal token in the environment variable `GITHUB_TOKEN`. That token needs to have the full `repo` OAuth scopes.
Adapt the GitHub user handle / lower / upper date / time limits as needed.
