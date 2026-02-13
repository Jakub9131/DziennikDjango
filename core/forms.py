from django import forms
from django.core.exceptions import ValidationError
from .models import User, ClassGroup, Subject
import re


def validate_only_letters(value):
    """Sprawdza, czy pole zawiera tylko litery, spacje i myślniki."""
    if not re.match(r'^[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s\-]+$', value):
        raise ValidationError("To pole może zawierać tylko litery.")


class ClassGroupForm(forms.ModelForm):
    class Meta:
        model = ClassGroup
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Np. 1A',
                'maxlength': '2'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name').upper().strip()
        if len(name) != 2:
            raise ValidationError("Nazwa klasy musi składać się dokładnie z 2 znaków (np. 1A).")
        if not re.match(r'^\d[A-ZĄĆĘŁŃÓŚŹŻ]$', name):
            raise ValidationError("Nazwa klasy musi zaczynać się cyfrą i kończyć literą (np. 1A).")
        return name

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Np. Matematyka'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise ValidationError("Nazwa przedmiotu musi mieć co najmniej 3 litery.")
        if not re.match(r'^[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s]+$', name):
            raise ValidationError("Nazwa przedmiotu może zawierać tylko litery.")
        return name

class TeacherCreationForm(forms.ModelForm):
    first_name = forms.CharField(
        validators=[validate_only_letters], 
        label="Imię",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Imię'})
    )
    last_name = forms.CharField(
        validators=[validate_only_letters], 
        label="Nazwisko",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nazwisko'})
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@szkola.pl'}),
        }

class StudentBasicForm(forms.ModelForm):
    first_name = forms.CharField(
        validators=[validate_only_letters], 
        label="Imię ucznia",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Imię ucznia'})
    )
    last_name = forms.CharField(
        validators=[validate_only_letters], 
        label="Nazwisko ucznia",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nazwisko ucznia'})
    )
    
    class_group = forms.ModelChoiceField(
        queryset=ClassGroup.objects.all(),
        label="Klasa ucznia",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'class_group']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email ucznia'}),
        }

class ParentBasicForm(forms.ModelForm):
    first_name = forms.CharField(
        validators=[validate_only_letters], 
        label="Imię rodzica",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Imię rodzica'})
    )
    last_name = forms.CharField(
        validators=[validate_only_letters], 
        label="Nazwisko rodzica",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nazwisko rodzica'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email rodzica'}),
        }

class AssignTeacherForm(forms.Form):
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(role='teacher'),
        label="Nauczyciel",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        label="Przedmiot",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class_group = forms.ModelChoiceField(
        queryset=ClassGroup.objects.all(),
        label="Klasa",
        widget=forms.Select(attrs={'class': 'form-control'})
    )