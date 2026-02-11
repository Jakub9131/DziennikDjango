from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from core.models import User, ClassGroup, Subject, SubjectAssignment, Grade
from django.db import transaction
import random

class Command(BaseCommand):
    help = 'Czyści bazę i generuje 5 przedmiotów, 9 klas, 10 nauczycieli, 45 uczniów oraz oceny.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Rozpoczynam proces (Clean & Seed)...")

        with transaction.atomic():
            # 1. CZYSZCZENIE BAZY (Kolejność ma znaczenie ze względu na klucze obce)
            self.stdout.write("Czyszczenie starej bazy danych...")
            Grade.objects.all().delete()
            SubjectAssignment.objects.all().delete()
            # Usuwamy tylko użytkowników, którzy NIE są superuserami (admin zostaje)
            User.objects.filter(is_superuser=False).delete()
            Subject.objects.all().delete()
            ClassGroup.objects.all().delete()

            # 2. TWORZENIE PRZEDMIOTÓW (5)
            self.stdout.write("Tworzenie przedmiotów...")
            subject_names = ['Matematyka', 'Język Polski', 'Język Angielski', 'Historia', 'Geografia']
            subjects = [Subject.objects.create(name=name) for name in subject_names]

            # 3. TWORZENIE KLAS (9: 1A, 1B, 1C, 2A, 2B, 2C, 3A, 3B, 3C)
            self.stdout.write("Tworzenie klas...")
            classes = []
            for year in range(1, 4):
                for letter in ['A', 'B', 'C']:
                    obj = ClassGroup.objects.create(name=f"{year}{letter}")
                    classes.append(obj)

            # 4. TWORZENIE NAUCZYCIELI (10)
            self.stdout.write("Tworzenie nauczycieli...")
            teachers = []
            for i in range(1, 11):
                email = f'nauczyciel{i}@szkola.pl'
                user = User.objects.create(
                    email=email,
                    username=email,
                    first_name=f'Nauczyciel{i}',
                    last_name=f'Kowalski{i}',
                    role='teacher',
                    password=make_password('nauczyciel123')
                )
                teachers.append(user)

            # 5. PRZYPISANIE NAUCZYCIELI
            # Każdy przedmiot w każdej klasie musi mieć nauczyciela, aby móc wystawić oceny
            self.stdout.write("Przypisywanie kadry do przedmiotów...")
            for cls in classes:
                for subj in subjects:
                    SubjectAssignment.objects.create(
                        teacher=random.choice(teachers),
                        subject=subj,
                        class_group=cls
                    )

            # 6. TWORZENIE UCZNIÓW, RODZICÓW I OCEN (45 duetów)
            self.stdout.write("Generowanie uczniów, rodziców i ocen (to chwilę potrwa)...")
            possible_values = [1, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6]
            comments = ["Aktywność", "Sprawdzian", "Kartkówka", "Zadanie domowe", "Odpowiedź"]
            
            student_global_idx = 1
            for cls in classes:
                for i in range(1, 6): # 5 uczniów na klasę (9 klas * 5 = 45)
                    # Rodzic
                    p_email = f'rodzic{student_global_idx}@poczta.pl'
                    parent = User.objects.create(
                        email=p_email,
                        username=p_email,
                        first_name=f'Rodzic{student_global_idx}',
                        last_name=f'Studentowski{student_global_idx}',
                        role='parent',
                        password=make_password('rodzic123')
                    )

                    # Uczeń
                    s_email = f'uczen{student_global_idx}@szkola.pl'
                    student = User.objects.create(
                        email=s_email,
                        username=s_email,
                        first_name=f'Student{student_global_idx}',
                        last_name=f'Studentowski{student_global_idx}',
                        role='student',
                        password=make_password('uczen123'),
                        parent=parent,
                        class_group=cls
                    )

                    # Wystawianie po 2 oceny z każdego przedmiotu
                    for subj in subjects:
                        # Pobieramy nauczyciela, który uczy daną klasę tego przedmiotu
                        assignment = SubjectAssignment.objects.get(class_group=cls, subject=subj)
                        
                        for _ in range(2):
                            Grade.objects.create(
                                student=student,
                                subject=subj,
                                teacher=assignment.teacher,
                                value=random.choice(possible_values),
                                comment=random.choice(comments)
                            )
                    
                    student_global_idx += 1

        self.stdout.write(self.style.SUCCESS('--- SEEDOWANIE ZAKOŃCZONE ---'))
        self.stdout.write(f'Stworzono: 5 przedmiotów, 9 klas, 10 nauczycieli, 45 uczniów i rodziców oraz 450 ocen.')