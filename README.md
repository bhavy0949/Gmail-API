# Gmail-API



- Initialize Python.sublime-build -> Google it
- In Python.sublime-build write the below code for running these scripts
- 
{
    "shell_cmd": "python -u /Users/bhavy/Downloads/fetchEmails.py && python -u /Users/bhavy/Downloads/api_call.py",
    "file_regex": "^[ ]*File \"(...*?)\", line ([0-9]*)",
    "selector": "source.python",
    "env": {"PYTHONIOENCODING": "utf-8"}
}
