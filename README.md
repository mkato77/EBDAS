# EBDAS

Balloon measurement data analysis software for balloons to be produced at the Balloon Festa in Tsukuba, a pre-public competition of Koshien of Science 2024.

# Installation
## Requirements
- Python 3.6 or later
- pip
- flet
- matplotlib
- numpy
- requests
- pyperclip

## Installation
To install the required packages, run the following command:

```
pip install flet matplotlib numpy requests pyperclip
```

# Usage
## Running the app
To run the app:

```
flet run [app_directory]
```

## Use damy local web server
To use damy local web server:

```
python server.py
```

and access to `http://localhost:8756/`.

You can run the software by setting `http://localhost:8756` from 編集>測定キット接続設定 in the app to imitate a measuring kit.
※ The default port number is 8756. If you want to change the port number, please change the number in the `server.py` file.

# License
This software will remain private until the end of the competition. Contributors (team members, advisors, and others) have a duty of confidentiality until the end of the tournament.