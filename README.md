# Gmail-API

## Enable the Gmail API and obtain the credentials:

- Go to the Google Developers Console: https://console.developers.google.com/
- Create a new project or select an existing one.
- Enable the Gmail API for the project.Create credentials for OAuth client ID.
- Download the JSON file containing the credentials.
- Place the downloaded JSON file in the same directory as the Python script and name it credentials.json.

## Initialize Python.sublime-build -> Google it
- In Python.sublime-build write the below code for running these scripts
- 
{
    "shell_cmd": "python -u /Users/bhavy/Downloads/fetchEmails.py && python -u /Users/bhavy/Downloads/api_call.py",
    "file_regex": "^[ ]*File \"(...*?)\", line ([0-9]*)",
    "selector": "source.python",
    "env": {"PYTHONIOENCODING": "utf-8"}
}
