from django.db import models
from django.contrib.auth.models import AbstractUser

class ClassGroup(models.Model):
    name = models.CharField(max_length=10, unique=True)
    def __str__(self): return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('student', 'Student'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    class_group = models.ForeignKey(ClassGroup, on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Grade(models.Model):
    VALUE_CHOICES = [
        (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades_received')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades_given')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    value = models.IntegerField(choices=VALUE_CHOICES)
    comment = models.CharField(max_length=255, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.last_name} - {self.subject.name}: {self.value}"

class SubjectAssignment(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('subject', 'class_group') 

    def __str__(self):
        return f"{self.subject.name} - {self.class_group.name} ({self.teacher.last_name})"