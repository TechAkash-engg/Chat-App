# AthrvEd-chat-application
Chat App Using Flask-SocketIO & Deployed in Heroku

# Introduction

An simple, reliable web chat application implemented using python-Flask-SocketIO with MongoDB and HTML/CSS, that provides fast Real-time messaging-share media & notifications with Synced chat backup, create-update-delete groups with admin access, upload profile & group pic with user friendly interface, and also has user registration-authentication functionalities, and many more features.

# Files in the repository

app.py: This is the main app file and contains both the registration/login page logic and the Flask-SocketIO backend for the app.

db.py: Contains functions regarding that database access and returns

user.py: Contains authorization and user credentials

Procfile: file required for Heroku

requirements.txt: list of Python packages installed (also required for Heroku)

templates/: folder with all HTML files needed for UI

static/: for with all images,icons,JS scripts and CSS files 

venv/: library and site packages needed

return_time.py: contains time limit for reset password
