Krok po kroku:

git clone https://github.com/Jakub9131/DziennikDjango
cd DziennikDjango

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate

python manage.py seed_data

python manage.py runserver