from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_admin_account(apps, schema_editor):
    User = apps.get_model('core', 'User')
    
    email = 'admin@szkola.pl'
    password = 'admin123'
    # Django wciąż potrzebuje username pod maską, ale nie będzie on używany do logowania
    username = 'admin_root' 

    # Teraz sprawdzamy po EMAILU, bo to on jest Twoim nowym identyfikatorem
    if not User.objects.filter(email=email).exists():
        User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_superuser=True,
            is_staff=True,
            is_active=True,
            role='admin' 
        )

def remove_admin_account(apps, schema_editor):
    User = apps.get_model('core', 'User')
    # Usuwamy po mailu, żeby było spójne
    User.objects.filter(email='admin@szkola.pl').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(create_admin_account, remove_admin_account),
    ]