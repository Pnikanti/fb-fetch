# FB-FETCH
Fetch 💩 from Facebook

# SETUP
touch .env @ root of project
populate following fields 

    APP_ID
    APP_SECRET
    USER_ID
    ACCESS_TOKEN

python -m venv venv
pip install -r requirements.txt

# RUNNING
source venv/bin/activate
python fb-fetch.py --help