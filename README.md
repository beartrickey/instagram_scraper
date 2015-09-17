# instagram_scraper
Public repository for Instragram scraping django app

Please follow the instructions below to setup and run this project:

DATABASE:
- run local postgres app (on port 5432)
- create database role "pixlee" (superuser, login)
- create database "pixlee"

PROJECT SETUP
- Make a virtual env with python 2.7.10 (run "virtualenv instagram_scraper_env")
- cd into instagram_env
- Activate the virtualenv (inside instagram_scraper_env, run "source bin/activate")
- Clone the repository
- cd into repository
- Run "pip install -r requirements.txt"
- Run "python manage.py migrate"

RUNNING THE APP
- Run "python manage.py runserver" (defaults to port 8000)
- Visit http://127.0.0.1:8000 in your browser (I've only confirmed on Chrome for the time being)
- Sign in to Instagram

- Enter job information:
 - Tag (without hashmark)
 - From date (exclusive)
 - To date (exclusive)
- Press "Submit"
- A new job should soon appear in the "Current Jobs" list on the right

REBOOTING JOBS
- Back in the terminal, ctrl-c to terminate your Django server. This will halt any running jobs.
- Restart the server with "python manage.py runserver". The jobs will still be halted, but should show up in the browser in the "Current Jobs" list.
- Press "Reboot Job" to restart selected jobs
- Jobs will disappear when they have paginated to a page with a tag time equal to the "From date"


NOTES:
- Files will be saved in /tmp/images/
- You can change this path by updating "MEDIA_ROOT" in pixlee_project/settings.py, and "upload_to" in pixlee_app/models.py (may require new migrations to be made)
