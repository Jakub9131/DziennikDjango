from django.contrib import admin
from .models import User, ClassGroup, Subject, Grade

admin.site.register(User)
admin.site.register(ClassGroup)
admin.site.register(Subject)
admin.site.register(Grade)