# JSN
## Prerequisites
- Python 3 (<= 3.11, as that version introduces breaking changes for some dependencies)
- MySQL
## Build instructions
1. Install the virtual environment library: pip install venv
2. Create a new virtual environment: python -m venv env
3. Activate the virtual environment: .\env\Scripts\activate
4. Install the required dependencies: pip install -r requirements/local.txt
5. Edit config/settings/common.py to reflect your local MySQL settings.
6. Run the database migrations:
    1. python manage.py makemigrations
    2. python manage.py migrate
7. Create a super user and follow the steps on screen: python manage.py createsuperuser
8. Execute the web server with: python manage.py runserver 8080